# PULSE - LLMOps Monitoring Dashboard

Production-oriented full-stack starter for tracking AI call health, latency, token usage, and estimated cost.

## Stack
- Backend: FastAPI + SQLite (`aiosqlite`)
- Frontend: React + Recharts
- AI Provider: Groq (`groq`)

## Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

## Frontend setup
```bash
cd frontend
npm install
npm start
```

## Live (currently running)
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Health: `http://localhost:8000/health`

## Endpoints
- `GET /health`
- `GET /metrics/summary`
- `GET /metrics/timeseries?hours=24`
- `GET /metrics/models`
- `GET /calls?limit=50&offset=0`
- `GET /calls/{id}`
- `GET /alerts`
- `POST /track`
- `POST /playground`
- `WS /ws`

## Phase 2 hardening included
- API key auth via `x-api-key` header (set `API_KEY` in backend env)
- In-memory per-IP rate limiting (`RATE_LIMIT_PER_MINUTE`)
- Dockerfiles for backend and frontend
- `docker-compose.yml` for local production-style run
- GitHub Actions CI for backend tests + frontend build
- Backend API smoke/security tests (`backend/tests`)

## Docker run
```bash
docker compose up --build
```

## Example App Demo (end-to-end)
This repo includes an example support bot app that uses Groq directly and pushes every call to PULSE via `POST /track`.

Run from the repo root (PowerShell):

```powershell
$env:GROQ_API_KEY="your_groq_key"
$env:PULSE_URL="http://localhost:8000"
python .\examples\support_bot_demo.py
```

What this demonstrates:
- A real app making LLM calls (support ticket responses)
- Per-call telemetry being ingested into PULSE
- Calls visible in dashboard and via `GET /calls`
