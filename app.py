from pathlib import Path

import joblib
import streamlit as st

MODEL_PATH = Path(__file__).parent / "model" / "sentiment_pipeline.joblib"

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


st.title("Real-Time Sentiment Analysis")
st.caption(
    "TF-IDF + Logistic Regression classifier, trained on 74k labeled tweets "
    "(95.2% validation accuracy) - a lightweight scikit-learn equivalent of "
    "the project's PySpark MLlib pipeline (see Spark/Spark-MLlib.py), used "
    "here so the model can run without a live Spark/Kafka/MongoDB cluster."
)

model = load_model()

if model is None:
    st.error(
        "Model file not found. Run `python train_model.py` first to train "
        "and save model/sentiment_pipeline.joblib."
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
            confidence = dict(zip(classes, proba))[prediction]

            style, emoji = SENTIMENT_STYLE.get(prediction, ("info", ""))
            getattr(st, style)(f"{emoji} **{prediction}** (confidence: {confidence:.1%})")

            with st.expander("Full probability breakdown"):
                st.bar_chart(dict(zip(classes, proba)))

st.divider()
st.caption(
    "This demo classifies a single piece of text on demand. The full "
    "real-time pipeline (Kafka producers -> Spark streaming -> MongoDB -> "
    "live dashboard) lives in `Spark/` and `Application - FLASK/` and "
    "requires that infrastructure to run - see the README for the "
    "`docker-compose up` instructions."
)
