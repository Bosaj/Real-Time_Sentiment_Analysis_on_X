# Monitoring, Controlling, Evaluation & QA Guide: Real-Time_Sentiment_Analysis_on_X

This document describes the standardized Observability, Health Control, Performance Evaluation, and Quality Assurance (QA) architecture for **Real-Time_Sentiment_Analysis_on_X**.

---

## 📊 1. Logs & Monitoring (Prometheus + Grafana)

### Structured Logging
Logs are formatted in structured JSON format for centralized ingestion:
- **Location**: `monitoring/logger.py` (or `monitoring/logger.js`)
- **Format**: JSON containing `timestamp`, `level`, `module`, `service`, and `message`.

### Prometheus Metrics Exporter
Prometheus metrics are exported on `/metrics` (or port 8000):
- **`app_requests_total`**: Counter tracking total incoming API requests by method, status, and endpoint.
- **`app_request_duration_seconds`**: Histogram measuring request latency distribution.
- **`model_evaluation_score`**: Gauge tracking accuracy, latency, and quality index scores.
- **`app_health_status`**: Gauge indicating liveness (1 = Healthy, 0 = Unhealthy).

### Grafana Dashboard & Scraper
- **Prometheus Scraper Config**: `monitoring/prometheus/prometheus.yml`
- **Grafana Dashboard JSON**: `monitoring/grafana/dashboard.json`
- Import `monitoring/grafana/dashboard.json` into Grafana to visualize request throughput, p95 latency, and model quality index in real time.

---

## 🎛️ 2. Health Controlling & Evaluation

### Health Check Controllers
Health and readiness control endpoints are located in `monitoring/health.py` (or `monitoring/health.js`):
- **Liveness (`/healthz`)**: Verifies process execution.
- **Readiness (`/readyz`)**: Verifies dependency availability.

### Evaluation Harness
Run the evaluation harness to compute performance index and accuracy metrics:
```bash
# For Python projects:
python -m scripts.eval_harness

# For Node.js projects:
node scripts/eval_harness.js
```

---

## 🧪 3. Quality Assurance (QA) & Testing

### Running Tests
- **Python Unit & QA Tests**: `pytest -v`
- **Configuration**: `pytest.ini`

### CI/CD Workflow
Automated testing, linting, evaluation, and observability validation run on every push to `main` via:
`.github/workflows/ci_qa_monitoring.yml`

---

## 🚀 Quick Reference Commands

| Task | Command |
| :--- | :--- |
| **Run QA Tests** | `pytest -v` |
| **Run Evaluation Harness** | `python -m scripts.eval_harness` |
| **Validate Monitoring Specs** | `test -f monitoring/grafana/dashboard.json` |
