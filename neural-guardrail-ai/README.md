# NeuralGuardrail-AI

NeuralGuardrail-AI is an end-to-end Python project that simulates API traffic, trains an LSTM-based anomaly detector, and exposes a FastAPI service that applies guardrail decisions of `ALLOW`, `THROTTLE`, or `BLOCK`.

## Features

- Synthetic API traffic generation with realistic anomaly patterns
- Sequence-aware feature engineering for LSTM training
- Supervised anomaly scoring model built with TensorFlow/Keras
- FastAPI inference endpoint with guardrail explanations
- SQLite request logging
- Optional Streamlit dashboard for score and decision trends
- Docker support
- Basic unit and API tests

## Project Structure

```text
neural-guardrail-ai/
├── api/
├── artifacts/
├── data_generator/
├── database/
├── model/
├── tests/
├── utils/
├── dashboard.py
├── Dockerfile
├── main.py
├── requirements.txt
└── train.py
```

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

## Generate Dataset

```bash
python -m data_generator.generator --rows 4000 --output artifacts/api_traffic.csv
```

Generated columns:

- `endpoint`
- `method`
- `response_time`
- `payload_size`
- `user_role`
- `timestamp`
- `is_anomaly`
- `anomaly_type`

## Train the Model

```bash
python train.py --data artifacts/api_traffic.csv --artifacts-dir artifacts
```

Saved artifacts:

- `artifacts/model.h5`
- `artifacts/preprocessor.joblib`
- `artifacts/metadata.joblib`

## Run the API Server

```bash
uvicorn main:app --reload
```

Endpoints:

- `GET /health`
- `POST /analyze`

## Sample Requests

### Normal request

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/api/products\",\"method\":\"GET\",\"response_time\":140,\"payload_size\":420,\"user_role\":\"user\"}"
```

### Malicious request

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/admin/config\",\"method\":\"POST\",\"response_time\":120,\"payload_size\":4500,\"user_role\":\"guest\"}"
```

### Edge case

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/api/upload\",\"method\":\"PUT\",\"response_time\":260,\"payload_size\":3900,\"user_role\":\"admin\"}"
```

## Logging

Every analyzed request is stored in SQLite at `artifacts/guardrail_logs.db` with:

- request metadata
- anomaly score
- decision
- explanation
- timestamp

## Optional Dashboard

```bash
streamlit run dashboard.py
```

The dashboard shows score trends and blocked/throttled totals from the SQLite logs.

## Run Tests

```bash
pytest
```

## Docker

```bash
docker build -t neural-guardrail-ai .
docker run -p 8000:8000 neural-guardrail-ai
```

## Notes

- Train the model before running the API if you want neural scoring enabled.
- If model artifacts do not exist yet, the API still runs in heuristic guardrail mode.
