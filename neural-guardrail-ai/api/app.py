"""FastAPI application exposing the anomaly guardrail service."""

from __future__ import annotations

from collections import Counter, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.decision_engine import apply_guardrail
from api.schemas import AnalyzeRequest, AnalyzeResponse
from database.sqlite_logger import init_db, log_request
from model.inference import InferenceService


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="NeuralGuardrail-AI", version="1.0.0", lifespan=lifespan)
inference_service = InferenceService()
recent_signatures: deque[tuple[str, str, str]] = deque(maxlen=50)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    payload = request.model_dump()
    signature = (payload["endpoint"], payload["method"], payload["user_role"])
    recent_signatures.append(signature)
    recent_count = Counter(recent_signatures)[signature]

    prediction = inference_service.append_and_score(payload)
    decision = apply_guardrail(
        model_score=prediction.anomaly_score,
        payload=payload,
        model_loaded=prediction.model_loaded,
        recent_identical_count=recent_count,
    )

    log_request(payload, decision.anomaly_score, decision.decision, decision.reason)
    return AnalyzeResponse(
        anomaly_score=decision.anomaly_score,
        decision=decision.decision,
        reason=decision.reason,
    )
