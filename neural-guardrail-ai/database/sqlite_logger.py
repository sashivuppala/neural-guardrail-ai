"""SQLite logging for analyzed requests."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from utils.config import settings


Base = declarative_base()


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    response_time = Column(Integer, nullable=False)
    payload_size = Column(Integer, nullable=False)
    user_role = Column(String, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    decision = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def log_request(payload: dict, score: float, decision: str, reason: str) -> None:
    session = SessionLocal()
    try:
        session.add(
            RequestLog(
                endpoint=payload["endpoint"],
                method=payload["method"],
                response_time=payload["response_time"],
                payload_size=payload["payload_size"],
                user_role=payload["user_role"],
                anomaly_score=score,
                decision=decision,
                reason=reason,
            )
        )
        session.commit()
    finally:
        session.close()


init_db()
