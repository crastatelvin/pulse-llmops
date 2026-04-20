import time
from groq import Groq
from analyzer import estimate_tokens, calculate_cost, score_prompt_quality, score_hallucination_risk
from settings import get_settings


def tracked_call(prompt: str, session_id: str = "default", model: str = "llama-3.1-8b-instant") -> dict:
    settings = get_settings()
    start = time.perf_counter()
    success = True
    response_text = ""
    error = ""
    input_tokens = 0
    output_tokens = 0

    try:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is missing")

        client = Groq(api_key=settings.groq_api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        response_text = completion.choices[0].message.content or ""
        if completion.usage:
            input_tokens = completion.usage.prompt_tokens or 0
            output_tokens = completion.usage.completion_tokens or 0
    except Exception as exc:
        success = False
        error = str(exc)

    if input_tokens == 0:
        input_tokens = estimate_tokens(prompt)
    if output_tokens == 0:
        output_tokens = estimate_tokens(response_text)

    total_tokens = input_tokens + output_tokens
    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "session_id": session_id,
        "model": model,
        "prompt": prompt,
        "response": response_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(latency_ms, 2),
        "cost_usd": calculate_cost(input_tokens, output_tokens),
        "error": error,
        "success": success,
        "prompt_quality_score": score_prompt_quality(prompt),
        "hallucination_risk": score_hallucination_risk(response_text) if success else 0,
    }
