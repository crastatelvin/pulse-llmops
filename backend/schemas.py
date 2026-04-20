from datetime import datetime
from pydantic import BaseModel, Field


class TrackCallRequest(BaseModel):
    session_id: str = "external"
    model: str = "unknown"
    prompt: str = ""
    response: str = ""
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0, ge=0)
    cost_usd: float = Field(default=0, ge=0)
    error: str = ""
    success: bool = True
    prompt_quality_score: float = Field(default=0, ge=0, le=100)
    hallucination_risk: float = Field(default=0, ge=0, le=100)
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime | None = None


class PlaygroundRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=16000)
    model: str = "llama-3.1-8b-instant"
    session_id: str = "playground"
