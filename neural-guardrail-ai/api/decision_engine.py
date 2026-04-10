"""Guardrail decision logic and explanations."""

from __future__ import annotations

from dataclasses import dataclass


ADMIN_ENDPOINT_PREFIXES = ("/admin", "/internal")


@dataclass
class DecisionResult:
    anomaly_score: float
    decision: str
    reason: str


def derive_reasons(payload: dict, recent_identical_count: int = 1) -> list[str]:
    reasons: list[str] = []
    endpoint = payload["endpoint"]
    method = payload["method"]
    payload_size = payload["payload_size"]
    response_time = payload["response_time"]
    user_role = payload["user_role"]

    if endpoint.startswith(ADMIN_ENDPOINT_PREFIXES) and user_role == "guest":
        reasons.append("unauthorized access")
    if payload_size >= 3500:
        reasons.append("abnormal payload")
    if response_time >= 650:
        reasons.append("response latency spike")
    if recent_identical_count >= 4:
        reasons.append("high-frequency burst")
    if endpoint.startswith("/noise/"):
        reasons.append("irregular endpoint pattern")
    if method == "DELETE" and user_role == "guest":
        reasons.append("destructive action by guest")
    return reasons


def heuristic_score(payload: dict, recent_identical_count: int = 1) -> float:
    score = 0.12
    reasons = derive_reasons(payload, recent_identical_count=recent_identical_count)
    severity_map = {
        "unauthorized access": 0.48,
        "abnormal payload": 0.22,
        "response latency spike": 0.12,
        "high-frequency burst": 0.2,
        "irregular endpoint pattern": 0.18,
        "destructive action by guest": 0.24,
    }
    for reason in reasons:
        score += severity_map.get(reason, 0.08)
    return max(0.0, min(1.0, score))


def apply_guardrail(
    model_score: float,
    payload: dict,
    model_loaded: bool = True,
    recent_identical_count: int = 1,
) -> DecisionResult:
    rules_score = heuristic_score(payload, recent_identical_count=recent_identical_count)
    anomaly_score = rules_score if not model_loaded else max(model_score, rules_score)

    if anomaly_score < 0.5:
        decision = "ALLOW"
    elif anomaly_score <= 0.8:
        decision = "THROTTLE"
    else:
        decision = "BLOCK"

    reasons = derive_reasons(payload, recent_identical_count=recent_identical_count)
    if not reasons:
        reasons = ["traffic pattern within baseline"]

    return DecisionResult(
        anomaly_score=round(anomaly_score, 4),
        decision=decision,
        reason=" + ".join(reasons),
    )
