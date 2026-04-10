from api.decision_engine import apply_guardrail


def test_guest_admin_request_is_blocked() -> None:
    payload = {
        "endpoint": "/admin/config",
        "method": "POST",
        "response_time": 95,
        "payload_size": 5500,
        "user_role": "guest",
    }

    result = apply_guardrail(0.1, payload, model_loaded=False, recent_identical_count=5)

    assert result.decision == "BLOCK"
    assert "unauthorized access" in result.reason


def test_normal_request_is_allowed() -> None:
    payload = {
        "endpoint": "/api/products",
        "method": "GET",
        "response_time": 110,
        "payload_size": 300,
        "user_role": "user",
    }

    result = apply_guardrail(0.22, payload, model_loaded=True, recent_identical_count=1)

    assert result.decision == "ALLOW"


def test_payload_spike_is_throttled_without_model() -> None:
    payload = {
        "endpoint": "/api/upload",
        "method": "PUT",
        "response_time": 260,
        "payload_size": 3900,
        "user_role": "admin",
    }

    result = apply_guardrail(0.1, payload, model_loaded=False, recent_identical_count=1)

    assert result.decision == "THROTTLE"
    assert result.reason == "abnormal payload"


def test_model_score_can_escalate_to_block() -> None:
    payload = {
        "endpoint": "/api/products",
        "method": "GET",
        "response_time": 120,
        "payload_size": 300,
        "user_role": "user",
    }

    result = apply_guardrail(0.91, payload, model_loaded=True, recent_identical_count=1)

    assert result.decision == "BLOCK"
    assert result.anomaly_score == 0.91
