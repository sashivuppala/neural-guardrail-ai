"""SQLite logging for analyzed requests."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine, func
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


def summarize_requests() -> dict:
    session = SessionLocal()
    try:
        total_requests = session.query(func.count(RequestLog.id)).scalar() or 0
        avg_score = session.query(func.avg(RequestLog.anomaly_score)).scalar()
        max_score = session.query(func.max(RequestLog.anomaly_score)).scalar()
        decision_rows = (
            session.query(RequestLog.decision, func.count(RequestLog.id))
            .group_by(RequestLog.decision)
            .all()
        )
        top_reason_rows = (
            session.query(RequestLog.reason, func.count(RequestLog.id))
            .group_by(RequestLog.reason)
            .order_by(func.count(RequestLog.id).desc())
            .limit(5)
            .all()
        )
        latest = session.query(func.max(RequestLog.created_at)).scalar()

        return {
            "total_requests": int(total_requests),
            "average_anomaly_score": round(float(avg_score or 0.0), 4),
            "max_anomaly_score": round(float(max_score or 0.0), 4),
            "decision_counts": {decision: int(count) for decision, count in decision_rows},
            "top_reasons": {reason: int(count) for reason, count in top_reason_rows},
            "last_request_at": latest.isoformat() if latest else None,
        }
    finally:
        session.close()


init_db()
