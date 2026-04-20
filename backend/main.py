import json
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from alert_engine import check_alerts
from database import (
    get_active_alerts,
    get_call_by_id,
    get_calls,
    get_metrics_summary,
    get_model_breakdown,
    get_timeseries,
    init_db,
    insert_call,
)
from groq_service import tracked_call
from rate_limiter import InMemoryRateLimiter
from schemas import PlaygroundRequest, TrackCallRequest
from settings import get_settings

app = FastAPI(title="PULSE LLMOps Monitoring Dashboard", version="1.0.0")
settings = get_settings()

logger = logging.getLogger("pulse")
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: list[WebSocket] = []
rate_limiter = InMemoryRateLimiter(limit=settings.rate_limit_per_minute)


async def broadcast(data: dict):
    dead: list[WebSocket] = []
    payload = json.dumps(data, default=str)
    for ws in connections:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in connections:
            connections.remove(ws)


@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("PULSE startup complete")


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    open_paths = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
    if request.url.path in open_paths:
        return await call_next(request)

    if settings.api_key:
        supplied = request.headers.get("x-api-key", "")
        if supplied != settings.api_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    client_host = request.client.host if request.client else "unknown"
    allowed = await rate_limiter.is_allowed(client_host)
    if not allowed:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    return await call_next(request)


@app.get("/")
def root():
    return {"status": "ok", "service": "pulse", "version": app.version}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/metrics/summary")
async def metrics_summary():
    return JSONResponse(await get_metrics_summary())


@app.get("/metrics/timeseries")
async def metrics_timeseries(hours: int = Query(24, ge=1, le=168)):
    return JSONResponse(await get_timeseries(hours))


@app.get("/metrics/models")
async def metrics_models():
    return JSONResponse(await get_model_breakdown())


@app.get("/calls")
async def list_calls(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    return JSONResponse(await get_calls(limit, offset))


@app.get("/calls/{call_id}")
async def get_call(call_id: int):
    call = await get_call_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return JSONResponse(call)


@app.get("/alerts")
async def list_alerts():
    return JSONResponse(await get_active_alerts())


@app.post("/track")
async def track_call(body: TrackCallRequest):
    payload = body.model_dump()
    if payload["total_tokens"] == 0:
        payload["total_tokens"] = payload["input_tokens"] + payload["output_tokens"]
    await insert_call(payload)
    await check_alerts(payload, broadcast)
    await broadcast({"event": "new_call", "call": payload})
    return {"tracked": True}


@app.post("/playground")
async def playground(body: PlaygroundRequest):
    result = tracked_call(prompt=body.prompt, session_id=body.session_id, model=body.model)
    await insert_call(result)
    await check_alerts(result, broadcast)
    await broadcast({"event": "new_call", "call": result})
    return JSONResponse(result)


@app.post("/demo/run-support")
async def run_support_demo():
    session_id = f"support-demo-{int(datetime.utcnow().timestamp())}"
    tickets = [
        "Customer says login link expired immediately after receiving it. Help draft a response.",
        "User reports invoice mismatch between dashboard and emailed receipt. Request details politely.",
        "Enterprise client asks for ETA on API latency fix after morning incident.",
    ]
    results = []
    for prompt in tickets:
        result = tracked_call(prompt=prompt, session_id=session_id, model="llama-3.1-8b-instant")
        await insert_call(result)
        await check_alerts(result, broadcast)
        await broadcast({"event": "new_call", "call": result})
        results.append(
            {
                "success": result["success"],
                "latency_ms": result["latency_ms"],
                "total_tokens": result["total_tokens"],
                "error": result["error"],
            }
        )

    return JSONResponse({"session_id": session_id, "count": len(results), "results": results})


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)
