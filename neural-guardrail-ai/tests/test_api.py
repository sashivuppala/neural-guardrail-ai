from fastapi.testclient import TestClient

from api.app import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "model_loaded" in response.json()


def test_analyze_returns_guardrail_decision() -> None:
    response = client.post(
        "/analyze",
        json={
            "endpoint": "/admin/config",
            "method": "POST",
            "response_time": 120,
            "payload_size": 4500,
            "user_role": "guest",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] in {"ALLOW", "THROTTLE", "BLOCK"}
    assert "anomaly_score" in body


def test_metrics_returns_operational_summary() -> None:
    client.post(
        "/analyze",
        json={
            "endpoint": "/admin/config",
            "method": "POST",
            "response_time": 120,
            "payload_size": 4500,
            "user_role": "guest",
        },
    )

    response = client.get("/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["total_requests"] >= 1
    assert "decision_counts" in body
    assert "top_reasons" in body
    assert "average_anomaly_score" in body
