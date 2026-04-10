from fastapi.testclient import TestClient

from api.app import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
