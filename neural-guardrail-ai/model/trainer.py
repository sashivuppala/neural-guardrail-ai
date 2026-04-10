"""Model training utilities."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

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
    probability_scores = model.predict(dataset.X_test, verbose=0).reshape(-1)
    predicted_labels = (probability_scores >= 0.5).astype(int)
    true_labels = dataset.y_test.astype(int)
    tn, fp, fn, tp = confusion_matrix(true_labels, predicted_labels, labels=[0, 1]).ravel()

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / settings.model_path.name
    preprocessor_path = artifacts_dir / settings.preprocessor_path.name
    metadata_path = artifacts_dir / settings.metadata_path.name
    evaluation_path = artifacts_dir / settings.evaluation_path.name

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
    evaluation = {
        "threshold": 0.5,
        "test_loss": round(float(loss), 4),
        "test_accuracy": round(float(accuracy), 4),
        "test_auc": round(float(auc), 4),
        "roc_auc_from_probabilities": round(float(roc_auc_score(true_labels, probability_scores)), 4),
        "precision": round(float(precision_score(true_labels, predicted_labels, zero_division=0)), 4),
        "recall": round(float(recall_score(true_labels, predicted_labels, zero_division=0)), 4),
        "f1_score": round(float(f1_score(true_labels, predicted_labels, zero_division=0)), 4),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "test_rows": int(len(true_labels)),
        "positive_rate": round(float(true_labels.mean()), 4),
    }
    evaluation_path.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")

    return {
        "model_path": str(model_path),
        "preprocessor_path": str(preprocessor_path),
        "metadata_path": str(metadata_path),
        "evaluation_path": str(evaluation_path),
        "test_loss": round(float(loss), 4),
        "test_accuracy": round(float(accuracy), 4),
        "test_auc": round(float(auc), 4),
        "test_f1": evaluation["f1_score"],
    }
