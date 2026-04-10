"""CLI for training the anomaly detection model."""

from __future__ import annotations

import argparse
from pathlib import Path

from data_generator.generator import generate_api_traffic
from model.trainer import train_and_save


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the NeuralGuardrail-AI LSTM model.")
    parser.add_argument("--data", type=str, default="artifacts/api_traffic.csv", help="Path to CSV dataset.")
    parser.add_argument("--artifacts-dir", type=str, default="artifacts", help="Directory for model artifacts.")
    parser.add_argument("--rows", type=int, default=4000, help="Rows to generate if dataset is missing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        print(f"Dataset not found at {data_path}. Generating {args.rows} synthetic rows...")
        df = generate_api_traffic(num_rows=args.rows)
        df.to_csv(data_path, index=False)

    summary = train_and_save(data_path=data_path, artifacts_dir=artifacts_dir)
    print("Training complete:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
