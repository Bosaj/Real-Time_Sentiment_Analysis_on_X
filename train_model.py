"""Train a lightweight sentiment classifier on the real training data.

This is a scikit-learn equivalent of the PySpark MLlib pipeline in
Spark/Spark-MLlib.py (TF-IDF features + a linear classifier), trained on
the same X_training.csv / X_validation.csv data. It exists so the model
can be deployed to Streamlit Community Cloud without needing a live
Spark/Kafka/MongoDB cluster - the real-time streaming pipeline in
Spark/ and Application - FLASK/ remains the intended production
architecture (see README) when that infrastructure is available.

Run: python train_model.py
Produces: model/sentiment_pipeline.joblib
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).parent
MODEL_DIR = ROOT / "model"
MODEL_PATH = MODEL_DIR / "sentiment_pipeline.joblib"

COLUMNS = ["TweetID", "Entity", "Sentiment", "Content"]


def load_split(name: str) -> pd.DataFrame:
    df = pd.read_csv(ROOT / "Spark" / name, header=None, names=COLUMNS)
    return df.dropna(subset=["Content"])


def main():
    train = load_split("X_training.csv")
    val = load_split("X_validation.csv")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=20000, ngram_range=(1, 2), stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000, C=5)),
    ])
    pipeline.fit(train["Content"], train["Sentiment"])

    pred = pipeline.predict(val["Content"])
    acc = accuracy_score(val["Sentiment"], pred)
    print(f"Validation accuracy: {acc:.4f}")
    print(classification_report(val["Sentiment"], pred))

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
