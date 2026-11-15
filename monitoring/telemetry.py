"""
Real-time sentiment telemetry tracker for rolling sentiment index,
velocity, and polarity spike detection over configurable temporal windows (#5).
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import math
import time
from typing import Deque, Dict, Iterable, List, Optional

POLARITY_WEIGHTS: Dict[str, float] = {
    "Positive": 1.0,
    "Negative": -1.0,
    "Neutral": 0.0,
    "Irrelevant": 0.0,
}


@dataclass(frozen=True)
class SentimentEvent:
    label: str
    confidence: float = 1.0
    timestamp: float = 0.0
    topic: str = "general"

    @property
    def weighted_score(self) -> float:
        base = POLARITY_WEIGHTS.get(self.label, 0.0)
        conf = max(0.0, min(1.0, float(self.confidence)))
        return base * conf


class SentimentTelemetryTracker:
    """Computes rolling sentiment index, velocity, and polarity spikes over a sliding window."""

    def __init__(self, window_seconds: float = 300.0, max_events: int = 10000) -> None:
        self.window_seconds = max(10.0, float(window_seconds))
        self._events: Deque[SentimentEvent] = deque(maxlen=max_events)

    def record(
        self,
        label: str,
        confidence: float = 1.0,
        timestamp: Optional[float] = None,
        topic: str = "general",
    ) -> SentimentEvent:
        ts = float(timestamp) if timestamp is not None else time.time()
        event = SentimentEvent(
            label=label,
            confidence=confidence,
            timestamp=ts,
            topic=topic,
        )
        self._events.append(event)
        return event

    def record_batch(self, events: Iterable[SentimentEvent]) -> int:
        count = 0
        for ev in events:
            self._events.append(ev)
            count += 1
        return count

    def active_events(self, now: Optional[float] = None, window_seconds: Optional[float] = None) -> List[SentimentEvent]:
        win = float(window_seconds) if window_seconds is not None else self.window_seconds
        if not self._events:
            return []
        ref_now = float(now) if now is not None else max(e.timestamp for e in self._events)
        cutoff = ref_now - win
        return [e for e in self._events if e.timestamp >= cutoff]

    def snapshot(self, now: Optional[float] = None, window_seconds: Optional[float] = None) -> Dict[str, object]:
        win = float(window_seconds) if window_seconds is not None else self.window_seconds
        events = self.active_events(now=now, window_seconds=win)
        total = len(events)
        if total == 0:
            return {
                "window_seconds": win,
                "sample_count": 0,
                "rolling_sentiment_index": 0.0,
                "sentiment_velocity": 0.0,
                "polarity_spike_zscore": 0.0,
                "polarity_spike_detected": False,
                "events_per_minute": 0.0,
                "class_counts": {"Positive": 0, "Negative": 0, "Neutral": 0, "Irrelevant": 0},
                "class_shares": {"Positive": 0.0, "Negative": 0.0, "Neutral": 0.0, "Irrelevant": 0.0},
            }

        scores = [e.weighted_score for e in events]
        rolling_index = sum(scores) / total

        # Split window into earlier half and recent half to compute sentiment velocity (per minute)
        ref_now = float(now) if now is not None else max(e.timestamp for e in events)
        midpoint = ref_now - (win / 2.0)
        early_scores = [e.weighted_score for e in events if e.timestamp < midpoint]
        recent_scores = [e.weighted_score for e in events if e.timestamp >= midpoint]

        if early_scores and recent_scores:
            early_mean = sum(early_scores) / len(early_scores)
            recent_mean = sum(recent_scores) / len(recent_scores)
        elif len(scores) >= 2:
            half = len(scores) // 2
            early_mean = sum(scores[:half]) / max(1, half)
            recent_mean = sum(scores[half:]) / max(1, len(scores) - half)
        else:
            early_mean = rolling_index
            recent_mean = rolling_index

        delta = recent_mean - early_mean
        half_window_minutes = max(0.25, (win / 2.0) / 60.0)
        velocity = delta / half_window_minutes

        # Compute polarity spike Z-score of recent tail (last 20% of events) vs baseline
        if len(scores) >= 5:
            tail_size = max(1, len(scores) // 5)
            baseline = scores[:-tail_size]
            tail = scores[-tail_size:]
            base_mean = sum(baseline) / len(baseline)
            variance = sum((x - base_mean) ** 2 for x in baseline) / max(1, len(baseline))
            std_dev = math.sqrt(variance) if variance > 1e-6 else 0.15
            tail_mean = sum(tail) / len(tail)
            z_score = (tail_mean - base_mean) / std_dev
        else:
            z_score = delta / 0.25 if abs(delta) > 0 else 0.0

        spike_detected = abs(z_score) >= 2.0 or abs(velocity) >= 0.35

        counts = Counter(e.label for e in events)
        class_counts = {
            "Positive": counts.get("Positive", 0),
            "Negative": counts.get("Negative", 0),
            "Neutral": counts.get("Neutral", 0),
            "Irrelevant": counts.get("Irrelevant", 0),
        }
        class_shares = {k: round(v / total, 4) for k, v in class_counts.items()}

        return {
            "window_seconds": win,
            "sample_count": total,
            "rolling_sentiment_index": round(rolling_index, 4),
            "sentiment_velocity": round(velocity, 4),
            "polarity_spike_zscore": round(z_score, 4),
            "polarity_spike_detected": bool(spike_detected),
            "events_per_minute": round(total / max(1.0 / 60.0, win / 60.0), 2),
            "class_counts": class_counts,
            "class_shares": class_shares,
        }

    def rolling_series(self, bucket_seconds: float = 30.0) -> List[Dict[str, float]]:
        """Generates a bucketed time-series of rolling sentiment index & velocity for Streamlit/Grafana charts."""
        if not self._events:
            return []
        ordered = sorted(self._events, key=lambda e: e.timestamp)
        start_ts = ordered[0].timestamp
        end_ts = ordered[-1].timestamp
        step = max(5.0, float(bucket_seconds))
        series: List[Dict[str, float]] = []
        cursor = start_ts + step
        prev_idx = 0.0
        while cursor <= end_ts + step:
            bucket = [e for e in ordered if (cursor - self.window_seconds) <= e.timestamp <= cursor]
            if bucket:
                idx = sum(e.weighted_score for e in bucket) / len(bucket)
                vel = idx - prev_idx
                prev_idx = idx
                series.append(
                    {
                        "timestamp": round(cursor, 2),
                        "rolling_sentiment_index": round(idx, 4),
                        "velocity": round(vel, 4),
                        "volume": float(len(bucket)),
                    }
                )
            cursor += step
        return series
