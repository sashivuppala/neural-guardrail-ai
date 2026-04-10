# NeuralGuardrail-AI Project Guide

## 1. What This Project Is

NeuralGuardrail-AI is an AI-powered API anomaly detection and guardrail system.

In simple terms, it acts like a smart security and monitoring layer for APIs:

- it watches incoming API traffic
- it looks for unusual or risky behavior
- it assigns an anomaly score
- it decides whether to `ALLOW`, `THROTTLE`, or `BLOCK` the request

This project is inspired by enterprise API security and runtime protection patterns, but it is built as a practical Python project that can be run locally for learning, demos, prototyping, and extension.

## 2. Who This Document Is For

This guide is written for both technical and non-technical readers.

- Non-technical readers can use it to understand what the project does, why it matters, and how the system behaves.
- Technical readers and developers can use it to understand the architecture, dependencies, setup, project structure, and implementation flow.

## 3. Why This Project Matters

Modern applications depend heavily on APIs. If APIs receive suspicious or abnormal requests, the impact can include:

- unauthorized access attempts
- abuse of sensitive endpoints
- oversized or malicious payloads
- burst traffic or bot-driven spikes
- degraded performance or service disruption

NeuralGuardrail-AI demonstrates how machine learning and rule-based logic can work together to reduce that risk.

## 4. What the System Does

The project has five major capabilities:

1. It generates synthetic API traffic data.
2. It engineers features from that traffic and converts it into sequences.
3. It trains an LSTM-based anomaly detection model.
4. It exposes a FastAPI service to analyze incoming requests.
5. It stores decisions in SQLite and optionally displays trends in Streamlit.

## 5. High-Level Flow

### Business-Friendly View

1. Simulate many API requests.
2. Teach the model what normal and abnormal behavior looks like.
3. Send a new request to the API.
4. Score the request for risk.
5. Return a guardrail action:

- `ALLOW` for low risk
- `THROTTLE` for medium risk
- `BLOCK` for high risk

### Technical View

1. Synthetic logs are generated with normal and anomalous patterns.
2. Categorical values are encoded and numeric values are normalized.
3. Request rows are converted into fixed-length time sequences.
4. An LSTM model is trained to predict anomaly likelihood.
5. At runtime, the API combines model output with rule-based heuristics.
6. Every analyzed request is logged in SQLite.

## 6. Core Use Cases

- API security demonstrations
- anomaly detection experimentation
- AI/ML learning projects
- guardrail engine prototypes
- interview or portfolio project demonstrations
- internal proof-of-concept security workflows

## 7. Example Decisions

### Example 1: Normal Request

Input:

```json
{
  "endpoint": "/api/products",
  "method": "GET",
  "response_time": 140,
  "payload_size": 420,
  "user_role": "user"
}
```

Typical outcome:

- low anomaly score
- decision: `ALLOW`

### Example 2: Suspicious Request

Input:

```json
{
  "endpoint": "/admin/config",
  "method": "POST",
  "response_time": 120,
  "payload_size": 4500,
  "user_role": "guest"
}
```

Typical outcome:

- high anomaly score
- decision: `BLOCK`
- reason may include `unauthorized access + abnormal payload`

## 8. Main Components

### 8.1 Data Generator

The data generator creates synthetic API logs with realistic traffic patterns.

Generated fields:

- `endpoint`
- `method`
- `response_time`
- `payload_size`
- `user_role`
- `timestamp`
- `is_anomaly`
- `anomaly_type`

Simulated anomaly patterns:

- guest users accessing admin endpoints
- high-frequency request bursts
- abnormal payload spikes
- irregular noise and unusual endpoint patterns

### 8.2 Feature Engineering

The preprocessing layer prepares raw API logs for machine learning:

- categorical features are one-hot encoded
- numeric values are normalized
- logs are converted into rolling sequences
- sequence tensors are produced for LSTM training and inference

### 8.3 ML Model

The project uses an LSTM neural network built with TensorFlow/Keras.

Why LSTM:

- API calls happen over time
- unusual behavior is often visible in sequences, not only single rows
- LSTMs are useful for learning time-dependent patterns

### 8.4 Guardrail Engine

The guardrail layer transforms anomaly scoring into business actions.

Decision thresholds:

- score `< 0.5` -> `ALLOW`
- score `0.5 to 0.8` -> `THROTTLE`
- score `> 0.8` -> `BLOCK`

The system also generates a readable explanation such as:

- `unauthorized access`
- `abnormal payload`
- `high-frequency burst`
- `traffic pattern within baseline`

### 8.5 API Layer

The FastAPI service exposes:

- `GET /health`
- `POST /analyze`

This is the runtime entry point for scoring live requests.

### 8.6 Logging Layer

Each analyzed request is stored in SQLite with:

- request details
- anomaly score
- decision
- reason
- timestamp

### 8.7 Dashboard

The optional Streamlit dashboard provides:

- anomaly score trends
- request decision breakdown
- blocked request counts
- throttled request counts

## 9. Technology Stack

### Core Platform

- Python `3.10+`
- Verified locally with Python `3.13`

### Frameworks and Libraries

- FastAPI `0.115.12`
- Uvicorn `0.34.0`
- TensorFlow `2.20.0`
- Keras `3.14.0`
- Pandas `2.2.3`
- NumPy `>=2.1.0,<3.0.0`
- Scikit-learn `1.6.1`
- Joblib `1.4.2`
- SQLAlchemy `2.0.40`
- Streamlit `1.44.1`
- Pytest `8.3.5`
- HTTPX `0.28.1`
- python-multipart `0.0.20`

### Storage

- SQLite

### Packaging / Runtime

- pip
- virtualenv via `python -m venv`

### Containerization

- Docker

## 10. Software and Package Reference

The project dependency file is:

- [requirements.txt](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\requirements.txt)

Current pinned or constrained packages:

```text
fastapi==0.115.12
uvicorn[standard]==0.34.0
tensorflow==2.20.0
pandas==2.2.3
numpy>=2.1.0,<3.0.0
scikit-learn==1.6.1
joblib==1.4.2
streamlit==1.44.1
sqlalchemy==2.0.40
python-multipart==0.0.20
pytest==8.3.5
httpx==0.28.1
```

## 11. Project Structure

```text
neural-guardrail-ai/
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── decision_engine.py
│   └── schemas.py
├── artifacts/
├── data_generator/
│   ├── __init__.py
│   └── generator.py
├── database/
│   ├── __init__.py
│   └── sqlite_logger.py
├── model/
│   ├── __init__.py
│   ├── inference.py
│   ├── preprocessing.py
│   └── trainer.py
├── tests/
│   ├── test_api.py
│   └── test_decision_engine.py
├── utils/
│   ├── __init__.py
│   └── config.py
├── .gitignore
├── dashboard.py
├── Dockerfile
├── main.py
├── PROJECT_GUIDE.md
├── README.md
├── requirements.txt
└── train.py
```

## 12. Developer-Oriented File Guide

### API Layer

- [app.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\api\app.py)
  Runs the FastAPI application and defines the runtime endpoints.

- [decision_engine.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\api\decision_engine.py)
  Contains decision thresholds, heuristic scoring, and reason generation.

- [schemas.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\api\schemas.py)
  Defines the request and response models for the API.

### Data Generation

- [generator.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\data_generator\generator.py)
  Generates synthetic normal and anomalous API traffic as CSV.

### Model Pipeline

- [preprocessing.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\model\preprocessing.py)
  Handles feature encoding, normalization, and sequence building.

- [trainer.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\model\trainer.py)
  Builds and trains the LSTM model, then saves artifacts.

- [inference.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\model\inference.py)
  Loads artifacts and performs live scoring using a rolling sequence buffer.

### Database

- [sqlite_logger.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\database\sqlite_logger.py)
  Creates the SQLite table and records analyzed requests.

### Shared Config

- [config.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\utils\config.py)
  Stores shared paths and default settings.

### Entrypoints

- [train.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\train.py)
  CLI entrypoint for training.

- [main.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\main.py)
  ASGI application entrypoint for Uvicorn.

- [dashboard.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\dashboard.py)
  Streamlit dashboard application.

## 13. How the Model Works

### Input Features

The model uses:

- endpoint
- method
- response time
- payload size
- user role

### Transformation Steps

1. Convert categories to machine-readable vectors.
2. Normalize numeric values.
3. Build fixed-length sequences of recent requests.
4. Feed those sequences into the LSTM network.

### Output

The model returns a score between `0` and `1`.

- lower scores indicate normal behavior
- higher scores indicate abnormal behavior

## 14. How the Guardrail Decision Is Made

The final decision is based on:

- model anomaly score
- rule-based heuristic checks

This hybrid approach helps the system remain practical:

- machine learning detects patterns
- rules explain obvious risks clearly
- explanations remain human-readable

## 15. Setup Instructions

### Recommended Local Setup

1. Open a terminal in the project root.
2. Create a virtual environment.
3. Activate the virtual environment.
4. Install dependencies.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Cross-Platform

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 16. How to Run the Project

### Step 1: Generate Synthetic Data

```bash
python -m data_generator.generator --rows 4000 --output artifacts/api_traffic.csv
```

### Step 2: Train the Model

```bash
python train.py --data artifacts/api_traffic.csv --artifacts-dir artifacts
```

Expected artifacts:

- `artifacts/model.h5`
- `artifacts/preprocessor.joblib`
- `artifacts/metadata.joblib`

### Step 3: Start the API

```bash
uvicorn main:app --reload
```

### Step 4: Test the API

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/admin/config\",\"method\":\"POST\",\"response_time\":120,\"payload_size\":4500,\"user_role\":\"guest\"}"
```

## 17. API Reference

### `GET /health`

Purpose:

- quick service availability check

Example response:

```json
{
  "status": "ok"
}
```

### `POST /analyze`

Purpose:

- analyze a request and return a guardrail action

Request body:

```json
{
  "endpoint": "/admin/config",
  "method": "POST",
  "response_time": 120,
  "payload_size": 4500,
  "user_role": "guest"
}
```

Response body:

```json
{
  "anomaly_score": 0.92,
  "decision": "BLOCK",
  "reason": "unauthorized access + abnormal payload"
}
```

## 18. Testing Guidance

Run tests with:

```bash
pytest
```

Included tests cover:

- guardrail decision logic
- API health endpoint
- API analyze endpoint behavior

## 19. Optional Dashboard

Start the dashboard with:

```bash
streamlit run dashboard.py
```

The dashboard reads from SQLite and displays:

- score trends over time
- blocked request counts
- throttled request counts
- recent decisions

## 20. Docker Usage

Build image:

```bash
docker build -t neural-guardrail-ai .
```

Run container:

```bash
docker run -p 8000:8000 neural-guardrail-ai
```

## 21. Output Artifacts

The `artifacts/` folder may contain:

- generated dataset CSV
- trained model file
- preprocessing object
- metadata file
- SQLite database
- runtime server logs

These are generated files and are intentionally excluded from source control.

## 22. Notes for Developers

### Design Pattern

The project uses a modular structure so each responsibility is isolated:

- generation
- preprocessing
- training
- inference
- decision logic
- API serving
- logging

### Why This Is Useful

This makes it easier to:

- replace the model
- change the anomaly rules
- switch the database
- add authentication
- add new endpoints
- build a richer dashboard

### Common Extension Ideas

- switch from HDF5 to native Keras model format
- add authentication and API keys
- use PostgreSQL instead of SQLite
- add rate-limiting middleware
- create a richer frontend UI
- add metrics and Prometheus support
- support batch analysis endpoints
- add CI/CD workflows

## 23. Notes for Non-Technical Stakeholders

This project should be viewed as a smart API protection demonstration system.

What it shows clearly:

- AI can help identify suspicious API behavior
- risky requests can be automatically acted on
- security decisions can still be explained in human-readable language
- logs and dashboards can make the system auditable

What it is not yet:

- a production-ready enterprise security platform
- a full IAM or API gateway replacement
- a complete SOC platform

It is best described as a strong prototype or demo-grade system with a real working architecture.

## 24. Quick Start Summary

If you only need the shortest path:

1. Install dependencies from `requirements.txt`.
2. Generate traffic data.
3. Train the model.
4. Start FastAPI with Uvicorn.
5. Send requests to `/analyze`.
6. Optionally open the Streamlit dashboard.

## 25. Where to Start If You Are New

### If You Are Non-Technical

Start with:

1. Section 1
2. Section 4
3. Section 5
4. Section 7
5. Section 23

### If You Are a Developer

Start with:

1. Section 11
2. Section 12
3. Section 15
4. Section 16
5. Section 17
6. [README.md](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\README.md)

## 26. Related Files

- [README.md](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\README.md)
- [train.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\train.py)
- [main.py](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\main.py)
- [requirements.txt](C:\Users\kiran\OneDrive\Documents\New project\neural-guardrail-ai\requirements.txt)

## 27. Final Summary

NeuralGuardrail-AI is a complete end-to-end project that combines:

- synthetic API traffic simulation
- sequence-based anomaly detection
- LSTM model training
- a guardrail decision engine
- a FastAPI scoring service
- SQLite logging
- optional Streamlit visualization
- Docker-based portability

It is intended to be understandable, demonstrable, extensible, and useful for both business explanation and technical implementation.
