"""Model training utilities."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from model.preprocessing import fit_transform_sequences, save_preprocessor
from utils.config import settings


def build_lstm_model(sequence_length: int, feature_count: int):
    from tensorflow import keras

    model = keras.Sequential(
        [
            keras.layers.Input(shape=(sequence_length, feature_count)),
            keras.layers.LSTM(64, return_sequences=True),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(32),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


def train_and_save(data_path: Path, artifacts_dir: Path) -> dict[str, float | str]:
    from tensorflow import keras

    df = pd.read_csv(data_path)
    dataset = fit_transform_sequences(df, sequence_length=settings.sequence_length)

    model = build_lstm_model(
        sequence_length=settings.sequence_length,
        feature_count=dataset.feature_count,
    )
    early_stopping = keras.callbacks.EarlyStopping(
        monitor="val_auc", mode="max", patience=3, restore_best_weights=True
    )
    history = model.fit(
        dataset.X_train,
        dataset.y_train,
        validation_data=(dataset.X_test, dataset.y_test),
        epochs=12,
        batch_size=32,
        verbose=0,
        callbacks=[early_stopping],
    )
    loss, accuracy, auc = model.evaluate(dataset.X_test, dataset.y_test, verbose=0)

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / settings.model_path.name
    preprocessor_path = artifacts_dir / settings.preprocessor_path.name
    metadata_path = artifacts_dir / settings.metadata_path.name

    model.save(model_path)
    save_preprocessor(dataset.preprocessor, str(preprocessor_path))
    joblib.dump(
        {
            "sequence_length": settings.sequence_length,
            "feature_count": dataset.feature_count,
            "epochs_ran": len(history.history["loss"]),
        },
        metadata_path,
    )

    return {
        "model_path": str(model_path),
        "preprocessor_path": str(preprocessor_path),
        "metadata_path": str(metadata_path),
        "test_loss": round(float(loss), 4),
        "test_accuracy": round(float(accuracy), 4),
        "test_auc": round(float(auc), 4),
    }
