import time
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metric Definitions for Real-Time_Sentiment_Analysis_on_X
REQUEST_COUNT = Counter("app_requests_total", "Total HTTP/API Requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("app_request_duration_seconds", "Request duration in seconds", ["endpoint"])
EVALUATION_SCORE = Gauge("model_evaluation_score", "Latest evaluation score", ["metric_name"])
APP_HEALTH_STATUS = Gauge("app_health_status", "Application health status (1=healthy, 0=unhealthy)")

def record_request(method, endpoint, status, duration):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

def update_eval_metric(name, value):
    EVALUATION_SCORE.labels(metric_name=name).set(value)

def set_health_status(is_healthy):
    APP_HEALTH_STATUS.set(1 if is_healthy else 0)

def start_metrics_exporter(port=8000):
    start_http_server(port)
    print(f"Metrics exporter running on port {port}")
