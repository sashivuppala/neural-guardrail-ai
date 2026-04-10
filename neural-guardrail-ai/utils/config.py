"""Shared project configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    sequence_length: int = 12
    dataset_path: Path = ARTIFACTS_DIR / "api_traffic.csv"
    model_path: Path = ARTIFACTS_DIR / "model.h5"
    preprocessor_path: Path = ARTIFACTS_DIR / "preprocessor.joblib"
    metadata_path: Path = ARTIFACTS_DIR / "metadata.joblib"
    database_url: str = f"sqlite:///{ARTIFACTS_DIR / 'guardrail_logs.db'}"
    random_seed: int = 42


settings = Settings()
