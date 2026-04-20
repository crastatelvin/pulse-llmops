import os
import time
from datetime import datetime, timezone

import requests
from groq import Groq


PULSE_URL = os.getenv("PULSE_URL", "http://localhost:8000")
PULSE_API_KEY = os.getenv("PULSE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if PULSE_API_KEY:
        headers["x-api-key"] = PULSE_API_KEY
    return headers


def tracked_support_reply(client: Groq, session_id: str, user_message: str) -> dict:
    started = time.perf_counter()
    success = True
    error = ""
    response_text = ""
    prompt_tokens = 0
    completion_tokens = 0

    system_prompt = (
        "You are a support assistant for a SaaS product. "
        "Reply in a practical, polite, and concise way."
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        response_text = completion.choices[0].message.content or ""
        if completion.usage:
            prompt_tokens = completion.usage.prompt_tokens or 0
            completion_tokens = completion.usage.completion_tokens or 0
    except Exception as exc:
        success = False
        error = str(exc)

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    total_tokens = prompt_tokens + completion_tokens
    tracked_payload = {
        "session_id": session_id,
        "model": MODEL,
        "prompt": user_message,
        "response": response_text,
        "input_tokens": prompt_tokens,
        "output_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
        "cost_usd": 0.0,  # PULSE can estimate cost independently if desired.
        "error": error,
        "success": success,
        "prompt_quality_score": 0,
        "hallucination_risk": 0,
        "metadata": {"source_app": "support-bot-demo"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    requests.post(
        f"{PULSE_URL}/track",
        json=tracked_payload,
        headers=_headers(),
        timeout=20,
    ).raise_for_status()

    return tracked_payload


def main():
    if not GROQ_API_KEY:
        raise RuntimeError("Set GROQ_API_KEY before running demo.")

    client = Groq(api_key=GROQ_API_KEY)
    session_id = f"support-demo-{int(time.time())}"
    tickets = [
        "Customer says login link expired immediately after receiving it. Help draft a response.",
        "User reports invoice mismatch between dashboard and emailed receipt. Request details politely.",
        "Enterprise client asks for ETA on API latency fix after morning incident.",
    ]

    print(f"Demo session: {session_id}")
    for idx, ticket in enumerate(tickets, start=1):
        result = tracked_support_reply(client, session_id, ticket)
        status = "OK" if result["success"] else "ERR"
        preview = (result["response"] or result["error"]).replace("\n", " ")[:120]
        print(
            f"{idx}. [{status}] latency={result['latency_ms']}ms "
            f"tokens={result['total_tokens']} preview={preview}"
        )

    print("Done. Open PULSE dashboard and check recent calls for this session.")


if __name__ == "__main__":
    main()
