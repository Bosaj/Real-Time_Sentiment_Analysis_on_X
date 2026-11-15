import json
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from monitoring.health import check_liveness, check_readiness, get_health_status
from monitoring.metrics import record_sentiment_telemetry
from monitoring.telemetry import SentimentTelemetryTracker
from scripts.eval_harness import run_evaluation


def test_liveness_and_readiness():
    assert check_liveness() is True
    assert check_readiness() is True


def test_health_status():
    status = get_health_status()
    assert status["status"] == "UP"
    assert status["service"] == "Real-Time_Sentiment_Analysis_on_X"


def test_eval_harness():
    results = run_evaluation()
    assert results["status"] == "PASSED"
    assert "quality_index" in results["metrics"]


def test_live_sentiment_telemetry_and_spike_detection():
    tracker = SentimentTelemetryTracker(window_seconds=120.0)
    base_ts = 1_700_000_000.0
    # Earlier window half: mostly negative
    for i in range(5):
        tracker.record("Negative", confidence=0.9, timestamp=base_ts + i * 5)
    # Recent window half: sharp positive spike
    for i in range(5):
        snap = record_sentiment_telemetry(
            "Positive",
            confidence=0.95,
            timestamp=base_ts + 70 + i * 5,
            tracker=tracker,
        )

    assert snap["sample_count"] == 10
    assert -1.0 <= snap["rolling_sentiment_index"] <= 1.0
    assert snap["sentiment_velocity"] > 0.5
    assert snap["polarity_spike_detected"] is True
    assert snap["class_counts"]["Positive"] == 5
    assert snap["class_counts"]["Negative"] == 5

    series = tracker.rolling_series(bucket_seconds=20.0)
    assert len(series) >= 3


def test_grafana_dashboard_telemetry_panels():
    dashboard_path = Path(__file__).resolve().parent.parent / "monitoring" / "grafana" / "dashboard.json"
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    titles = [p["title"] for p in dashboard["panels"]]
    assert any("Rolling Sentiment Index" in t for t in titles)
    assert any("Sentiment Velocity" in t for t in titles)
    assert any("Polarity" in t for t in titles)
