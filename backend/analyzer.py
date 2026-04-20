import re
from settings import get_settings


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    settings = get_settings()
    input_cost = (input_tokens / 1000) * settings.cost_per_1k_input_tokens
    output_cost = (output_tokens / 1000) * settings.cost_per_1k_output_tokens
    return round(input_cost + output_cost, 8)


def score_prompt_quality(prompt: str) -> float:
    score = 50.0
    words = len(prompt.split())
    if words < 5:
        score -= 20
    elif words > 10:
        score += 10
    if words > 50:
        score += 10

    specificity_words = [
        "specifically",
        "exactly",
        "format",
        "list",
        "explain",
        "analyze",
        "compare",
        "provide",
        "generate",
        "summarize",
    ]
    for word in specificity_words:
        if word in prompt.lower():
            score += 5

    if any(w in prompt.lower() for w in ["context:", "background:", "you are", "your role"]):
        score += 10
    if "?" in prompt:
        score += 5
    if prompt.strip().endswith("."):
        score += 3

    return min(100.0, max(0.0, round(score, 1)))


def score_hallucination_risk(response: str) -> float:
    risk = 20.0
    for phrase in ["according to", "research shows", "studies indicate", "the data"]:
        if phrase in response.lower():
            risk -= 5
    for phrase in ["i think", "i believe", "probably", "might be", "could be", "not sure"]:
        if phrase in response.lower():
            risk += 8
    if len(response.split()) < 10:
        risk += 15
    if len(re.findall(r"\b\d+\.?\d*%?\b", response)) > 3:
        risk += 10
    return min(100.0, max(0.0, round(risk, 1)))
