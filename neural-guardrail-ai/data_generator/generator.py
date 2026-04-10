"""Generate synthetic API traffic with enterprise-style anomalies."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from utils.config import settings


ENDPOINTS = [
    "/api/products",
    "/api/orders",
    "/api/search",
    "/api/cart",
    "/api/upload",
    "/admin/config",
    "/admin/users",
    "/internal/metrics",
]
METHODS = ["GET", "POST", "PUT", "DELETE"]
ROLES = ["admin", "user", "guest"]
ADMIN_ENDPOINTS = {"/admin/config", "/admin/users", "/internal/metrics"}


@dataclass
class TrafficPattern:
    endpoint: str
    method: str
    response_time: int
    payload_size: int
    user_role: str
    timestamp: datetime
    is_anomaly: int
    anomaly_type: str


def _normal_request(current_time: datetime, rng: np.random.Generator) -> TrafficPattern:
    endpoint = rng.choice(ENDPOINTS, p=[0.2, 0.2, 0.18, 0.14, 0.12, 0.06, 0.05, 0.05]).item()
    method = rng.choice(METHODS, p=[0.45, 0.3, 0.15, 0.1]).item()
    user_role = rng.choice(ROLES, p=[0.1, 0.72, 0.18]).item()

    if endpoint in ADMIN_ENDPOINTS and user_role != "admin":
        user_role = "admin"

    response_time = int(np.clip(rng.normal(loc=180, scale=55), 40, 700))
    payload_center = 450 if method == "GET" else 900
    payload_size = int(np.clip(rng.normal(loc=payload_center, scale=180), 50, 2500))

    return TrafficPattern(
        endpoint=endpoint,
        method=method,
        response_time=response_time,
        payload_size=payload_size,
        user_role=user_role,
        timestamp=current_time,
        is_anomaly=0,
        anomaly_type="normal",
    )


def _unauthorized_request(current_time: datetime, rng: np.random.Generator) -> TrafficPattern:
    endpoint = rng.choice(list(ADMIN_ENDPOINTS)).item()
    method = rng.choice(["POST", "PUT", "DELETE"], p=[0.5, 0.3, 0.2]).item()
    response_time = int(np.clip(rng.normal(loc=95, scale=20), 20, 220))
    payload_size = int(np.clip(rng.normal(loc=3500, scale=900), 700, 6500))
    return TrafficPattern(
        endpoint=endpoint,
        method=method,
        response_time=response_time,
        payload_size=payload_size,
        user_role="guest",
        timestamp=current_time,
        is_anomaly=1,
        anomaly_type="unauthorized_access",
    )


def _payload_spike(current_time: datetime, rng: np.random.Generator) -> TrafficPattern:
    pattern = _normal_request(current_time, rng)
    pattern.payload_size = int(np.clip(rng.normal(loc=6000, scale=1400), 2800, 12000))
    pattern.response_time = int(np.clip(rng.normal(loc=420, scale=90), 120, 1300))
    pattern.is_anomaly = 1
    pattern.anomaly_type = "abnormal_payload"
    return pattern


def _noise_request(current_time: datetime, rng: np.random.Generator) -> TrafficPattern:
    endpoint = f"/noise/{rng.integers(100, 999)}"
    method = rng.choice(METHODS).item()
    user_role = rng.choice(ROLES).item()
    response_time = int(np.clip(rng.normal(loc=700, scale=260), 30, 2200))
    payload_size = int(np.clip(rng.normal(loc=2500, scale=1600), 10, 10000))
    return TrafficPattern(
        endpoint=endpoint,
        method=method,
        response_time=response_time,
        payload_size=payload_size,
        user_role=user_role,
        timestamp=current_time,
        is_anomaly=1,
        anomaly_type="irregular_pattern",
    )


def _burst_requests(base_time: datetime, rng: np.random.Generator, size: int = 6) -> Iterable[TrafficPattern]:
    endpoint = rng.choice(["/api/search", "/api/orders", "/admin/config"], p=[0.45, 0.35, 0.2]).item()
    role = "guest" if endpoint == "/admin/config" else rng.choice(["user", "guest"], p=[0.7, 0.3]).item()
    for offset in range(size):
        yield TrafficPattern(
            endpoint=endpoint,
            method="POST" if endpoint != "/api/search" else "GET",
            response_time=int(np.clip(rng.normal(loc=80, scale=15), 10, 200)),
            payload_size=int(np.clip(rng.normal(loc=2400, scale=700), 200, 7000)),
            user_role=role,
            timestamp=base_time + timedelta(seconds=offset),
            is_anomaly=1,
            anomaly_type="high_frequency_burst",
        )


def generate_api_traffic(num_rows: int = 4000, seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(settings.random_seed if seed is None else seed)
    current_time = datetime.utcnow() - timedelta(minutes=num_rows)
    records: list[TrafficPattern] = []

    while len(records) < num_rows:
        current_time += timedelta(seconds=int(rng.integers(5, 40)))
        anomaly_draw = rng.random()
        if anomaly_draw < 0.08:
            records.append(_unauthorized_request(current_time, rng))
        elif anomaly_draw < 0.16:
            records.append(_payload_spike(current_time, rng))
        elif anomaly_draw < 0.22:
            records.extend(_burst_requests(current_time, rng, size=int(rng.integers(4, 8))))
        elif anomaly_draw < 0.27:
            records.append(_noise_request(current_time, rng))
        else:
            records.append(_normal_request(current_time, rng))

    trimmed = records[:num_rows]
    df = pd.DataFrame([pattern.__dict__ for pattern in trimmed])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic API traffic.")
    parser.add_argument("--rows", type=int, default=4000, help="Number of rows to generate.")
    parser.add_argument("--output", type=str, default=str(settings.dataset_path), help="Output CSV path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_api_traffic(num_rows=args.rows)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows at {output_path}")


if __name__ == "__main__":
    main()
