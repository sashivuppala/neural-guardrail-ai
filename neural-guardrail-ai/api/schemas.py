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
