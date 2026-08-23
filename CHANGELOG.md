# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `app.py` + `train_model.py`: a lightweight, deployable Streamlit demo. Trains a scikit-learn TF-IDF + Logistic Regression pipeline on the same `Spark/X_training.csv` data as the PySpark pipeline (95.2% accuracy on `Spark/X_validation.csv`), so the sentiment classifier can be tried and deployed (e.g. Streamlit Community Cloud) without a live Kafka/Spark/MongoDB stack. The full real-time pipeline remains the intended production architecture when that infrastructure is available.
- Split `requirements.txt` into a lightweight root file (for `app.py`/Streamlit Cloud) and `requirements-pipeline.txt` (the original full pipeline dependencies); CI now installs and validates both.
- MIT `LICENSE` file (the README already referenced an MIT license; the file itself was missing).
- `requirements.txt` pinning the project's runtime dependencies (PySpark, kafka-python, Flask, PyMongo, pandas, python-dotenv, certifi, requests).
- GitHub Actions CI workflow validating notebook integrity, Python syntax, and dependency installability (does not spin up Kafka/Spark/MongoDB).
- Testing/CI and Changelog sections in `README.md`.

### Security
- Removed the tracked `.env` file from version control (it contained a live database connection string). `.env` is git-ignored going forward; only `.env.example` with placeholder values is tracked. **The previously committed credential should be rotated**, since it remains visible in this repository's git history.

## [v1.0] - 2025-12-29

Initial tagged release: end-to-end real-time sentiment analysis pipeline for Twitter/X streams.

### Added
- Kafka producer/consumer setup for streaming tweets (from a CSV dataset or manual input).
- Spark Streaming + Spark MLlib pipeline: `Tokenizer -> StopWordsRemover -> HashingTF -> IDF -> LogisticRegression` (with a Naive Bayes model as a backup), trained on a 1.6M-tweet dataset ([Kaggle Twitter Entity Sentiment Analysis](https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis)), classifying tweets as Positive / Negative / Neutral / Irrelevant.
- MongoDB persistence of sentiment predictions with metadata.
- Flask web application with a live streaming dashboard, a manual tweet-submission endpoint, and a historical results table.
- Optional LLM-based classification path using Groq.
- Docker Compose setup for Kafka + Zookeeper, and a Dockerfile for a Spark/Jupyter image.
- Demonstration video and project presentation.

Full release notes: https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X/releases/tag/v1.0
