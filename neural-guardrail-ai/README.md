# NeuralGuardrail-AI

NeuralGuardrail-AI is an end-to-end API protection prototype that detects suspicious API behavior and returns explainable runtime decisions: `ALLOW`, `THROTTLE`, or `BLOCK`.

It combines synthetic traffic generation, LSTM-based anomaly scoring, heuristic guardrail rules, FastAPI serving, SQLite audit logging, Streamlit monitoring, Docker support, and automated tests.

## Why It Stands Out

- Sequence-aware anomaly detection for API request behavior
- Hybrid neural and rule-based scoring for explainable decisions
- Safe fallback mode when model artifacts are not available
- Operational `/metrics` endpoint for runtime observability
- Training evaluation artifact with AUC, precision, recall, F1, and confusion matrix
- SQLite decision audit trail
- Dashboard for model quality, traffic trends, decision counts, and top reasons
- Clean modular structure suitable for demos, interviews, and extension

## Architecture

```text
Synthetic Traffic -> Preprocessing -> LSTM Training -> Saved Artifacts
                                      |
Incoming Request -> FastAPI -> Inference + Rules -> Guardrail Decision
                                      |
                            SQLite Logs + Metrics + Dashboard
```

## Project Structure

```text
neural-guardrail-ai/
├── api/
│   ├── app.py
│   ├── decision_engine.py
│   └── schemas.py
├── data_generator/
│   └── generator.py
├── database/
│   └── sqlite_logger.py
├── model/
│   ├── inference.py
│   ├── preprocessing.py
│   └── trainer.py
├── tests/
│   ├── test_api.py
│   └── test_decision_engine.py
├── utils/
│   └── config.py
├── dashboard.py
├── Dockerfile
├── main.py
├── PROJECT_GUIDE.md
├── DEMO_SCENARIOS.md
├── requirements.txt
└── train.py
```

## Setup

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

## Generate Data

```bash
python -m data_generator.generator --rows 4000 --output artifacts/api_traffic.csv
```

Generated fields:

- `endpoint`
- `method`
- `response_time`
- `payload_size`
- `user_role`
- `timestamp`
- `is_anomaly`
- `anomaly_type`

## Train The Model

```bash
python train.py --data artifacts/api_traffic.csv --artifacts-dir artifacts
```

Saved artifacts:

- `artifacts/model.h5`
- `artifacts/preprocessor.joblib`
- `artifacts/metadata.joblib`
- `artifacts/evaluation.json`

The evaluation file includes:

- test loss
- test accuracy
- test AUC
- precision
- recall
- F1 score
- confusion matrix
- positive class rate

## Run The API

```bash
uvicorn main:app --reload
```

Endpoints:

- `GET /health`
- `GET /metrics`
- `POST /analyze`

## Sample Requests

Normal request:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/api/products\",\"method\":\"GET\",\"response_time\":140,\"payload_size\":420,\"user_role\":\"user\"}"
```

Suspicious request:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/admin/config\",\"method\":\"POST\",\"response_time\":120,\"payload_size\":4500,\"user_role\":\"guest\"}"
```

Operational metrics:

```bash
curl "http://127.0.0.1:8000/metrics"
```

## Dashboard

```bash
streamlit run dashboard.py
```

The dashboard shows:

- model evaluation summary
- total analyzed requests
- blocked and throttled counts
- average and max anomaly score
- decision distribution
- top guardrail reasons
- anomaly score trend
- recent decision log

## Run Tests

```bash
pytest
```

## Docker

```bash
docker build -t neural-guardrail-ai .
docker run -p 8000:8000 neural-guardrail-ai
```

## Positioning

NeuralGuardrail-AI is best described as a strong prototype for AI-assisted API security. It is intentionally small enough to understand, but complete enough to demonstrate the full lifecycle from data simulation to model training, live scoring, explainable action, logging, monitoring, and testing.
