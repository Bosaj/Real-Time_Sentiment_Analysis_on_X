# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
