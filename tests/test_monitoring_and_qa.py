import pytest
from monitoring.health import check_liveness, check_readiness, get_health_status
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
