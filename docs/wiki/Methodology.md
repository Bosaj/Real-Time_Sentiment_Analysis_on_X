# Methodology

## Dataset

The [Kaggle Twitter Entity Sentiment Analysis](https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis) dataset provides:

- **Training set** (`X_training.csv`): 1.6 million labeled tweets with columns `tweet_id`, `entity` (product/brand mentioned), `sentiment`, and `content`.
- **Validation set** (`X_validation.csv`): 500K tweets in the same format, used to simulate a live tweet stream.

Labels: Negative (0), Positive (1), Neutral (2), Irrelevant (3).

## Preprocessing pipeline

Built with Spark MLlib transformers, chained as:

```
Tokenizer -> StopWordsRemover -> HashingTF -> IDF
```

- **Tokenizer**: splits tweet text into words.
- **StopWordsRemover**: drops common words ("the", "is", "at", ...).
- **HashingTF**: hashes tokens into a fixed-size feature vector (8,192 features).
- **IDF**: re-weights those features by inverse document frequency.

## Model

`LogisticRegression(maxIter=100, regParam=0.01)` trained on the TF-IDF features, with a Naive Bayes model trained alongside as a backup/comparison (`NaiveBayes_Model_V1`).

## Evaluation

On the held-out validation data:

| Metric | Value |
|---|---|
| Accuracy | 82% |
| Precision | 0.81 |
| Recall | 0.80 |
| F1-score | 0.80 |

## Real-time inference

```
Tweet -> Preprocessing (Tokenizer/StopWords/HashingTF/IDF) -> Classification -> MongoDB
```

Average end-to-end latency is 1–3 seconds per tweet, with a measured throughput of 20–50 tweets/second and MongoDB insert times of 0.2–0.5 seconds. An optional LLM-based classification path via Groq exists alongside the Spark MLlib model, gated behind the `GROQ_API_KEY` environment variable — it is not the primary classification path.

## A note on the removed credential

An earlier commit in this repository's history had a real MongoDB connection string committed in a tracked `.env` file. It has since been removed from tracking; `.env` is now git-ignored and only `.env.example` (placeholder values) is committed. Any wiki or documentation content referencing environment configuration for this project should use placeholder variable names (`MONGO_URI`, `GROQ_API_KEY`, etc.) only — never a real connection string or credential.
