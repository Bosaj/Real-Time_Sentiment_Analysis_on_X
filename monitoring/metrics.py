from prometheus_client import Counter, Gauge, Histogram, start_http_server

from monitoring.telemetry import SentimentTelemetryTracker

# Metric Definitions for Real-Time_Sentiment_Analysis_on_X
REQUEST_COUNT = Counter("app_requests_total", "Total HTTP/API Requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("app_request_duration_seconds", "Request duration in seconds", ["endpoint"])
EVALUATION_SCORE = Gauge("model_evaluation_score", "Latest evaluation score", ["metric_name"])
APP_HEALTH_STATUS = Gauge("app_health_status", "Application health status (1=healthy, 0=unhealthy)")

# Live Sentiment Telemetry Metrics (#5)
SENTIMENT_PREDICTIONS_TOTAL = Counter(
    "sentiment_predictions_total",
    "Total classified tweets by sentiment polarity",
    ["polarity"],
)
ROLLING_SENTIMENT_INDEX = Gauge(
    "sentiment_rolling_index",
    "Rolling weighted sentiment polarity index (-1.0 to +1.0)",
    ["window"],
)
SENTIMENT_VELOCITY = Gauge(
    "sentiment_velocity_per_min",
    "Rate of change of rolling sentiment index per minute",
    ["window"],
)
POLARITY_SPIKE_ZSCORE = Gauge(
    "sentiment_polarity_spike_zscore",
    "Z-score of recent polarity spike relative to rolling window baseline",
    ["window"],
)

DEFAULT_TRACKER = SentimentTelemetryTracker(window_seconds=300.0)


def record_request(method, endpoint, status, duration):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)


def update_eval_metric(name, value):
    EVALUATION_SCORE.labels(metric_name=name).set(value)


def set_health_status(is_healthy):
    APP_HEALTH_STATUS.set(1 if is_healthy else 0)


def record_sentiment_telemetry(label, confidence=1.0, timestamp=None, topic="general", tracker=None):
    active_tracker = tracker or DEFAULT_TRACKER
    active_tracker.record(label=label, confidence=confidence, timestamp=timestamp, topic=topic)
    SENTIMENT_PREDICTIONS_TOTAL.labels(polarity=label).inc()
    snap = active_tracker.snapshot(now=timestamp)
    window_label = f"{int(snap['window_seconds'])}s"
    ROLLING_SENTIMENT_INDEX.labels(window=window_label).set(float(snap["rolling_sentiment_index"]))
    SENTIMENT_VELOCITY.labels(window=window_label).set(float(snap["sentiment_velocity"]))
    POLARITY_SPIKE_ZSCORE.labels(window=window_label).set(float(snap["polarity_spike_zscore"]))
    return snap


def start_metrics_exporter(port=8000):
    start_http_server(port)
    print(f"Metrics exporter running on port {port}")
