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
