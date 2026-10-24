# Architecture and Design: Real-Time_Sentiment_Analysis_on_X

## 🏗️ Architectural Diagram
```mermaid
graph TD
    UI["Application UI / Entrypoint"] --> Core["Core Logic Engine"]
    Core --> Obs["Monitoring & Health System"]
    Obs --> Prom["Prometheus Metrics (/metrics)"]
    Obs --> Graf["Grafana Dashboard Spec"]
    Core --> Test["Pytest / Vitest QA Harness"]
```

## 📦 Directory Structure
- `monitoring/`: Structured logger, Prometheus configs, Grafana dashboards, health probes
- `scripts/eval_harness.py`: Synthetic evaluation & latency score harness
- `tests/test_monitoring_and_qa.py`: QA test suite
- `.github/workflows/ci_qa_monitoring.yml`: Automated CI pipeline
