"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    endpoint: str = Field(..., examples=["/admin/config"])
    method: Literal["GET", "POST", "PUT", "DELETE"]
    response_time: int = Field(..., ge=0, examples=[120])
    payload_size: int = Field(..., ge=0, examples=[4500])
    user_role: Literal["admin", "user", "guest"]


class AnalyzeResponse(BaseModel):
    anomaly_score: float
    decision: Literal["ALLOW", "THROTTLE", "BLOCK"]
    reason: str


class MetricsResponse(BaseModel):
    total_requests: int
    average_anomaly_score: float
    max_anomaly_score: float
    decision_counts: dict[str, int]
    top_reasons: dict[str, int]
    last_request_at: str | None
