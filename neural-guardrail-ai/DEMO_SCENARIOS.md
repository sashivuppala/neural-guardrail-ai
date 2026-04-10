# Demo Scenarios

Use these scenarios to show the system moving from normal traffic to suspicious behavior, with explainable guardrail actions and observable metrics.

## 1. Health And Model Status

```bash
curl "http://127.0.0.1:8000/health"
```

What to show:

- service is reachable
- `model_loaded` confirms whether neural scoring is active
- the system still works in heuristic fallback mode if artifacts are missing

## 2. Normal User Traffic

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/api/products\",\"method\":\"GET\",\"response_time\":140,\"payload_size\":420,\"user_role\":\"user\"}"
```

Expected result:

- decision: `ALLOW`
- reason: `traffic pattern within baseline`
- low anomaly score

## 3. Payload Spike

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/api/upload\",\"method\":\"PUT\",\"response_time\":260,\"payload_size\":3900,\"user_role\":\"admin\"}"
```

Expected result:

- decision: `THROTTLE`
- reason: `abnormal payload`
- medium anomaly score

## 4. Guest Accessing Admin Endpoint

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/admin/config\",\"method\":\"POST\",\"response_time\":120,\"payload_size\":4500,\"user_role\":\"guest\"}"
```

Expected result:

- decision: `BLOCK`
- reason includes `unauthorized access`
- high anomaly score

## 5. Repeated Burst Pattern

Run the same request at least four times:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"endpoint\":\"/api/search\",\"method\":\"GET\",\"response_time\":80,\"payload_size\":2400,\"user_role\":\"guest\"}"
```

Expected result:

- later requests include `high-frequency burst`
- the decision can escalate as repeated behavior accumulates

## 6. Operational Metrics

```bash
curl "http://127.0.0.1:8000/metrics"
```

What to show:

- total request count
- average and max anomaly score
- decision breakdown
- top guardrail reasons
- timestamp of the last analyzed request

## 7. Dashboard Walkthrough

```bash
streamlit run dashboard.py
```

What to show:

- model evaluation quality
- blocked and throttled activity
- score trends over time
- recent audit trail
- top risk reasons
