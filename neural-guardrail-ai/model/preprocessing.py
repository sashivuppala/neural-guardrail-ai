"""Feature engineering and sequence preparation utilities."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

from utils.config import settings


FEATURE_COLUMNS = ["endpoint", "method", "response_time", "payload_size", "user_role"]
CATEGORICAL_COLUMNS = ["endpoint", "method", "user_role"]
NUMERIC_COLUMNS = ["response_time", "payload_size"]


@dataclass
class SequenceDataset:
    X_train: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    preprocessor: Pipeline
    feature_count: int


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_COLUMNS,
            ),
            ("numeric", MinMaxScaler(), NUMERIC_COLUMNS),
        ]
    )


def fit_transform_sequences(
    dataframe: pd.DataFrame,
    sequence_length: int = settings.sequence_length,
) -> SequenceDataset:
    df = dataframe.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    preprocessor = build_preprocessor()
    transformed = preprocessor.fit_transform(df[FEATURE_COLUMNS])
    transformed_array = np.asarray(transformed, dtype=np.float32)
    labels = df["is_anomaly"].astype(np.float32).to_numpy()

    sequences: list[np.ndarray] = []
    sequence_labels: list[float] = []
    for idx in range(sequence_length - 1, len(df)):
        window = transformed_array[idx - sequence_length + 1 : idx + 1]
        sequences.append(window)
        sequence_labels.append(labels[idx])

    X = np.stack(sequences)
    y = np.asarray(sequence_labels, dtype=np.float32)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    return SequenceDataset(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        preprocessor=preprocessor,
        feature_count=X.shape[2],
    )


def transform_requests(
    requests_df: pd.DataFrame,
    preprocessor: Pipeline,
) -> np.ndarray:
    transformed = preprocessor.transform(requests_df[FEATURE_COLUMNS])
    return np.asarray(transformed, dtype=np.float32)


class RequestSequenceBuffer:
    """Maintain a rolling window for live inference."""

    def __init__(self, sequence_length: int = settings.sequence_length) -> None:
        self.sequence_length = sequence_length
        self._buffer: deque[dict[str, Any]] = deque(maxlen=sequence_length)

    def append(self, payload: dict[str, Any]) -> None:
        self._buffer.append(payload)

    def as_dataframe(self) -> pd.DataFrame:
        if not self._buffer:
            return pd.DataFrame(columns=FEATURE_COLUMNS)
        rows = list(self._buffer)
        if len(rows) < self.sequence_length:
            pad_count = self.sequence_length - len(rows)
            rows = [rows[0]] * pad_count + rows
        return pd.DataFrame(rows)


def save_preprocessor(preprocessor: Pipeline, path: str) -> None:
    joblib.dump(preprocessor, path)


def load_preprocessor(path: str) -> Pipeline:
    return joblib.load(path)
