# NeuralGuardrail-AI Project Guide

## 1. What This Project Is

NeuralGuardrail-AI is an AI-assisted API anomaly detection and guardrail system.

It watches API request metadata, estimates risk, explains why a request looks suspicious, and returns one of three runtime actions:

- `ALLOW`
- `THROTTLE`
- `BLOCK`

The project is built as a practical prototype for security demos, portfolio reviews, interviews, and future production hardening.

## 2. Why It Matters

Modern applications depend on APIs. Risky API behavior can include:

- guest users attempting admin actions
- oversized payloads
- burst traffic or bot-like repetition
- irregular endpoint patterns
- destructive methods from low-trust users
- response latency spikes

NeuralGuardrail-AI demonstrates how machine learning and deterministic rules can work together to detect and explain this behavior.

## 3. High-Level Flow

```text
Synthetic API Logs
  -> preprocessing and sequence building
  -> LSTM model training
  -> saved model artifacts

Incoming API Request
  -> FastAPI service
  -> neural score plus heuristic rules
  -> ALLOW, THROTTLE, or BLOCK
  -> SQLite audit log
  -> metrics endpoint and dashboard
```

## 4. Core Capabilities

- Generate synthetic API traffic with labeled anomaly patterns
- Train an LSTM model on rolling request sequences
- Save model, preprocessor, metadata, and evaluation artifacts
- Analyze live request metadata through FastAPI
- Explain guardrail decisions in human-readable language
- Fall back to rule-based scoring if model artifacts are missing
- Log every decision to SQLite
- Expose runtime metrics through `/metrics`
- Display model and operational trends in Streamlit
- Run through Docker and automated tests

## 5. Main Components

### Data Generator

`data_generator/generator.py` creates realistic API request rows with:

- endpoint
- method
- response time
- payload size
- user role
- timestamp
- anomaly label
- anomaly type

Simulated anomaly types include unauthorized access, payload spikes, burst traffic, and irregular endpoint patterns.

### Preprocessing

`model/preprocessing.py` handles:

- one-hot encoding for categorical fields
- numeric scaling
- rolling sequence construction
- live inference buffering

### LSTM Model

`model/trainer.py` trains a TensorFlow/Keras LSTM model and saves:

- `artifacts/model.h5`
- `artifacts/preprocessor.joblib`
- `artifacts/metadata.joblib`
- `artifacts/evaluation.json`

`evaluation.json` includes test loss, accuracy, AUC, precision, recall, F1 score, confusion matrix, test row count, and positive class rate.

### Inference Service

`model/inference.py` loads model artifacts and scores live request sequences. If loading fails, the API continues in heuristic fallback mode.

### Guardrail Engine

`api/decision_engine.py` converts risk signals into decisions:

- score below `0.5`: `ALLOW`
- score from `0.5` through `0.8`: `THROTTLE`
- score above `0.8`: `BLOCK`

The engine explains decisions with reasons such as:

- `unauthorized access`
- `abnormal payload`
- `response latency spike`
- `high-frequency burst`
- `irregular endpoint pattern`
- `destructive action by guest`

### API

`api/app.py` exposes:

- `GET /health`
- `GET /metrics`
- `POST /analyze`

### Logging And Metrics

`database/sqlite_logger.py` stores analyzed requests and produces operational summaries:

- total requests
- average anomaly score
- max anomaly score
- decision counts
- top reasons
- last request timestamp

### Dashboard

`dashboard.py` shows:

- model evaluation summary
- total request volume
- blocked and throttled counts
- average and max anomaly score
- decision distribution
- top guardrail reasons
- anomaly score trend
- recent decision log

## 6. Project Structure

```text
neural-guardrail-ai/
+-- api/
|   +-- app.py
|   +-- decision_engine.py
|   +-- schemas.py
+-- data_generator/
|   +-- generator.py
+-- database/
|   +-- sqlite_logger.py
+-- model/
|   +-- inference.py
|   +-- preprocessing.py
|   +-- trainer.py
+-- tests/
|   +-- test_api.py
|   +-- test_decision_engine.py
+-- utils/
|   +-- config.py
+-- dashboard.py
+-- DEMO_SCENARIOS.md
+-- Dockerfile
+-- main.py
+-- README.md
+-- requirements.txt
+-- train.py
```

## 7. Quick Start

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Generate data:

```bash
python -m data_generator.generator --rows 4000 --output artifacts/api_traffic.csv
```

Train the model:

```bash
python train.py --data artifacts/api_traffic.csv --artifacts-dir artifacts
```

Run the API:

```bash
uvicorn main:app --reload
```

Run tests:

```bash
pytest
```

Run the dashboard:

```bash
streamlit run dashboard.py
```

## 8. API Reference

### `GET /health`

Returns service status and whether model artifacts loaded.

Example response:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### `POST /analyze`

Analyzes a request and returns a guardrail decision.

Example request:

```json
{
  "endpoint": "/admin/config",
  "method": "POST",
  "response_time": 120,
  "payload_size": 4500,
  "user_role": "guest"
}
```

Example response:

```json
{
  "anomaly_score": 0.92,
  "decision": "BLOCK",
  "reason": "unauthorized access + abnormal payload"
}
```

### `GET /metrics`

Returns operational metrics from the SQLite audit log.

Example response:

```json
{
  "total_requests": 25,
  "average_anomaly_score": 0.4212,
  "max_anomaly_score": 1.0,
  "decision_counts": {
    "ALLOW": 14,
    "THROTTLE": 6,
    "BLOCK": 5
  },
  "top_reasons": {
    "traffic pattern within baseline": 14,
    "unauthorized access + abnormal payload": 5
  },
  "last_request_at": "2026-04-10T21:10:00"
}
```

## 9. Demo Scenarios

Use `DEMO_SCENARIOS.md` to walk through:

- health and model status
- normal traffic
- payload spike throttling
- guest admin access blocking
- repeated burst detection
- operational metrics
- dashboard monitoring

## 10. Current Maturity

This project is a strong prototype, not a production gateway replacement.

Strong today:

- full end-to-end ML and API workflow
- clear explainability
- fallback behavior
- audit logging
- runtime metrics
- dashboard
- Docker support
- automated tests

Production hardening still to add:

- authentication and API keys
- external database support
- model registry or versioning
- Prometheus/OpenTelemetry export
- CI/CD workflow
- load testing
- real traffic replay integration
- richer alerting

## 11. Final Positioning

NeuralGuardrail-AI is best presented as an AI-powered API guardrail prototype that demonstrates the full lifecycle: data simulation, model training, live inference, explainable policy action, audit logging, metrics, dashboarding, and tests.
