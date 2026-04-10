"""Inference service for anomaly scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
from pandas import DataFrame

from model.preprocessing import RequestSequenceBuffer, load_preprocessor, transform_requests
from utils.config import settings


@dataclass
class PredictionResult:
    anomaly_score: float
    model_loaded: bool


class InferenceService:
    def __init__(self) -> None:
        self.sequence_buffer = RequestSequenceBuffer(sequence_length=settings.sequence_length)
        self.model = None
        self.preprocessor = None
        self.metadata: dict[str, Any] = {}
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        try:
            from tensorflow import keras

            self.model = keras.models.load_model(settings.model_path)
            self.preprocessor = load_preprocessor(str(settings.preprocessor_path))
            self.metadata = joblib.load(settings.metadata_path)
        except Exception:
            self.model = None
            self.preprocessor = None
            self.metadata = {}

    def append_and_score(self, payload: dict[str, Any]) -> PredictionResult:
        self.sequence_buffer.append(payload)
        if self.model is None or self.preprocessor is None:
            return PredictionResult(anomaly_score=0.0, model_loaded=False)

        frame: DataFrame = self.sequence_buffer.as_dataframe()
        transformed = transform_requests(frame, self.preprocessor)
        sequence = np.expand_dims(transformed, axis=0)
        score = float(self.model.predict(sequence, verbose=0)[0][0])
        return PredictionResult(anomaly_score=score, model_loaded=True)
