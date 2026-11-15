import json
from pathlib import Path
import time

import joblib
import streamlit as st

from monitoring.metrics import record_sentiment_telemetry
from monitoring.telemetry import SentimentEvent, SentimentTelemetryTracker

MODEL_PATH = Path(__file__).parent / "model" / "sentiment_pipeline.joblib"
GRAFANA_DASHBOARD_PATH = Path(__file__).parent / "monitoring" / "grafana" / "dashboard.json"

SENTIMENT_STYLE = {
    "Positive": ("success", "🙂"),
    "Negative": ("error", "🙁"),
    "Neutral": ("info", "😐"),
    "Irrelevant": ("warning", "❓"),
}


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def get_session_tracker(window_seconds: float) -> SentimentTelemetryTracker:
    if "sentiment_tracker" not in st.session_state:
        tracker = SentimentTelemetryTracker(window_seconds=window_seconds)
        now = time.time()
        seed_samples = [
            ("Positive", 0.92, now - 240, "Borderlands"),
            ("Positive", 0.88, now - 210, "Borderlands"),
            ("Neutral", 0.79, now - 180, "Nvidia"),
            ("Negative", 0.91, now - 150, "ServerOutage"),
            ("Positive", 0.95, now - 110, "Borderlands"),
            ("Positive", 0.94, now - 75, "Borderlands"),
            ("Positive", 0.97, now - 35, "ReleaseDay"),
            ("Positive", 0.96, now - 10, "ReleaseDay"),
        ]
        tracker.record_batch(
            SentimentEvent(label=lbl, confidence=conf, timestamp=ts, topic=tpc)
            for lbl, conf, ts, tpc in seed_samples
        )
        st.session_state["sentiment_tracker"] = tracker
    tracker = st.session_state["sentiment_tracker"]
    tracker.window_seconds = window_seconds
    return tracker


st.title("Real-Time Sentiment Analysis & Live Telemetry")
st.caption(
    "TF-IDF + Logistic Regression classifier trained on 74k labeled tweets "
    "(95.2% validation accuracy) with real-time rolling sentiment index, "
    "velocity, and polarity spike telemetry."
)

tab_classify, tab_telemetry = st.tabs(
    ["Single Tweet Classifier", "Live Telemetry & Grafana Dashboard (#5)"]
)

model = load_model()

with tab_classify:
    if model is None:
        st.error(
            "Model file not found. Run `python train_model.py` first to train and save model/sentiment_pipeline.joblib."
        )
    else:
        text = st.text_area(
            "Enter text to classify",
            value="I am coming to the borders and I will kill you all in Borderlands!",
            height=100,
        )

        if st.button("Analyze sentiment"):
            if not text.strip():
                st.warning("Please enter some text.")
            else:
                prediction = model.predict([text])[0]
                proba = model.predict_proba([text])[0]
                classes = model.named_steps["clf"].classes_
                confidence = float(dict(zip(classes, proba, strict=False))[prediction])

                tracker = get_session_tracker(300.0)
                record_sentiment_telemetry(
                    label=prediction,
                    confidence=confidence,
                    timestamp=time.time(),
                    tracker=tracker,
                )

                style, emoji = SENTIMENT_STYLE.get(prediction, ("info", ""))
                getattr(st, style)(f"{emoji} **{prediction}** (confidence: {confidence:.1%})")

                with st.expander("Full probability breakdown"):
                    st.bar_chart(dict(zip(classes, proba, strict=False)))

with tab_telemetry:
    window_choice = st.selectbox(
        "Temporal Sliding Window",
        options=[("1 Minute (60s)", 60.0), ("5 Minutes (300s)", 300.0), ("15 Minutes (900s)", 900.0)],
        index=1,
        format_func=lambda item: item[0],
    )
    tracker = get_session_tracker(window_choice[1])
    snap = tracker.snapshot(now=time.time(), window_seconds=window_choice[1])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rolling Sentiment Index", f"{snap['rolling_sentiment_index']:+.2f}")
    col2.metric("Sentiment Velocity (/min)", f"{snap['sentiment_velocity']:+.2f}")
    col3.metric("Polarity Spike Z-Score", f"{snap['polarity_spike_zscore']:+.2f}")
    col4.metric("Throughput (events/min)", f"{snap['events_per_minute']:.1f}")

    if snap["polarity_spike_detected"]:
        st.warning(
            f"Polarity Spike Detected! Z-Score={snap['polarity_spike_zscore']:+.2f}, "
            f"Velocity={snap['sentiment_velocity']:+.2f}/min"
        )
    else:
        st.success("Stream polarity within normal variance bounds.")

    series = tracker.rolling_series(bucket_seconds=30.0)
    if series:
        st.subheader("Rolling Sentiment Index & Velocity Over Time")
        st.line_chart(
            {
                "rolling_sentiment_index": [row["rolling_sentiment_index"] for row in series],
                "velocity": [row["velocity"] for row in series],
            }
        )

    st.subheader("Polarity Class Distribution in Active Window")
    st.bar_chart(snap["class_counts"])

    if GRAFANA_DASHBOARD_PATH.exists():
        with st.expander("Grafana Provisioned Dashboard Specification (monitoring/grafana/dashboard.json)"):
            st.json(json.loads(GRAFANA_DASHBOARD_PATH.read_text(encoding="utf-8")))

st.divider()
st.caption(
    "This dashboard tracks live classifications and exports Prometheus/Grafana metrics (`sentiment_rolling_index`, "
    "`sentiment_velocity_per_min`, `sentiment_polarity_spike_zscore`). The full Kafka/Spark/MongoDB pipeline lives "
    "in `Spark/` and `Application - FLASK/`."
)
