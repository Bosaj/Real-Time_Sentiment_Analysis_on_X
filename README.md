# Real-Time Sentiment Analysis on Twitter/X Streams

[![CI](https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X/actions/workflows/ci.yml/badge.svg)](https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-FDEE21?style=for-the-badge&logo=apachespark&logoColor=black)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000?style=for-the-badge&logo=apachekafka)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

- **ELHADJI Oussama**
- **BEN ACHA Yassine**
- **CHAKOR Abdellatif**
- **MENACH Achraf**

***

## ⚡ Try it now — lightweight demo (no infrastructure required)

The full pipeline below needs a live Kafka + Spark + MongoDB stack. For a version you can actually run and deploy with nothing but Python, `app.py` wraps a scikit-learn TF-IDF + Logistic Regression model — trained on the exact same `Spark/X_training.csv` data (74,682 labeled tweets) as the PySpark pipeline — behind a Streamlit UI. It reaches **95.2% validation accuracy** on `Spark/X_validation.csv`.

```bash
pip install -r requirements.txt   # lightweight deps only: streamlit, scikit-learn, pandas, joblib
python train_model.py             # trains and saves model/sentiment_pipeline.joblib (~5.6MB)
streamlit run app.py
```

Deployable in one click at [share.streamlit.io](https://share.streamlit.io) (point it at `app.py`) — no Docker, Kafka, or MongoDB needed. Note: the underlying model is trained on gaming/tech-brand Twitter commentary, so it's strong within that domain but can misclassify unrelated neutral text (e.g. plain scheduling statements) — a real limitation of the training data, not the demo itself.

***

## 📋 Overview
This project is a **real-time sentiment analysis web application** that processes Twitter/X streams using Apache Kafka, Apache Spark MLlib, and machine learning models. The system classifies each tweet into four sentiment categories:
- ✅ **Positive**
- ❌ **Negative**
- ⚪ **Neutral**
- 🔵 **Irrelevant**

### Key Features
- 🔄 Real-time streaming data pipeline with Kafka
- 🤖 Machine learning-based sentiment classification (Logistic Regression)
- 📊 Interactive web dashboard with live predictions
- 💾 MongoDB storage for historical analysis
- 🎨 Modern glassmorphism UI with dark/light mode
- ⚡ Low-latency processing (1-3 seconds per tweet)

***

## 🎥 Demonstration

### Watch the Complete System in Action

<div align="center">

**[📹 Watch Full Demo Video (MP4)](https://github.com/user-attachments/assets/07d26b77-38c3-4219-8956-0ff7f9da89e7)**

<sub>⏱️ Duration: ~5 minutes | 📺 Quality: 1080p | 💾 Size: ~45MB</sub>

</div>

---


## 🏗️ System Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Kafka     │─────▶│   Spark     │─────▶│   MongoDB   │◀─────│    Flask    │
│  Producer   │      │  Streaming  │      │   Database  │      │   Web App   │
│  (Tweets)   │      │  (ML Model) │      │  (Results)  │      │  (UI/API)   │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
```

### Components
1. **Kafka Producer** - Streams tweets from Twitter API or CSV files
2. **Spark Streaming** - Processes tweets using ML models (TF-IDF + Logistic Regression)
3. **MongoDB** - Stores sentiment predictions with metadata
4. **Flask Web Application** - Provides real-time dashboard and API endpoints

***

## 📁 Project Structure

```
Real-Time_Sentiment_Analysis_on_X/
├── app.py                         # Lightweight Streamlit demo (deployable, no infra needed)
├── train_model.py                 # Trains the scikit-learn model behind app.py
├── model/sentiment_pipeline.joblib # Saved model (95.2% validation accuracy)
├── requirements.txt                # Lightweight deps for app.py / Streamlit Cloud
├── requirements-pipeline.txt       # Full deps for the real-time pipeline below
├── Application - FLASK/
│   ├── main.py                    # Flask application
│   ├── templates/
│   │   ├── header.html           # Navigation header
│   │   ├── index.html            # Homepage
│   │   ├── streaming.html        # Live stream dashboard
│   │   └── validation.html       # Results table
│   └── static/
│       ├── css/
│       │   └── style.css         # Modern UI styling
│       └── js/
│           └── main.js           # Client-side logic
├── Spark/
│   ├── Spark-MLlib.py            # Model training script
│   ├── KafkaSpark-Streaming.py   # Real-time processing
│   ├── KafkaProducer-Streaming.py # Tweet producer
│   ├── X_training.csv            # Training dataset (1.6M tweets)
│   ├── X_validation.csv          # Validation dataset
│   ├── IDF_V1/                   # TF-IDF model
│   ├── V1/                       # Logistic Regression model
│   └── NaiveBayes_Model_V1/      # Naive Bayes model (backup)
├── docker-compose.yml             # Kafka + Zookeeper setup
├── Dockerfile                     # Spark-Jupyter image
├── .env                          # Environment variables
└── README.md                     # This file
```

***

## 🚀 Setup Instructions

### Prerequisites
- **Docker** & **Docker Compose** (for Kafka)
- **Python 3.11** (for Spark compatibility)
- **MongoDB** (local or Atlas)
- **Java 11** (for Spark)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X.git
cd Real-Time_Sentiment_Analysis_on_X
```

### 2️⃣ Environment Setup

Copy `.env.example` to `.env` and fill in your own values:
```bash
cp .env.example .env
```
```env
MONGO_URI=mongodb://localhost:27017/
GROQ_API_KEY=your_groq_api_key   # only needed for the optional LLM classification path
PYTHONIOENCODING=utf-8
HADOOP_HOME=C:\hadoop
PYSPARK_PYTHON=C:\Users\YourUser\AppData\Local\Programs\Python\Python311\python.exe
PYSPARK_DRIVER_PYTHON=C:\Users\YourUser\AppData\Local\Programs\Python\Python311\python.exe
```

> **Never commit your real `.env` file.** It is git-ignored; only `.env.example` (with placeholder values) is tracked.

### 3️⃣ Install Python Dependencies

For the full real-time pipeline (Kafka/Spark/MongoDB/Flask) described in this section:
```bash
pip install -r requirements-pipeline.txt
```

(`requirements.txt` at the repo root is intentionally the lightweight set for the Streamlit demo above — streamlit, scikit-learn, pandas, joblib — so it installs fast on Streamlit Community Cloud, which always reads the root file.)

### 4️⃣ Start Kafka with Docker

```bash
docker-compose up -d
```

**Verify Kafka is running:**
```bash
docker ps
```

You should see:
- `kafka` container on port `9092`
- `zookeeper` container on port `2181`

### 5️⃣ Start MongoDB

**Option A: Local MongoDB**
```bash
mongod --dbpath /path/to/data
```

**Option B: MongoDB Atlas**
Update `.env` with your Atlas connection string:
```env
MONGO_URI=
```

### 6️⃣ Train the Machine Learning Models

```bash
cd Spark
python Spark-MLlib.py
```

**Expected output:**
```
Training model...
Model accuracy: 0.82
Saving models to:
  - IDF_V1/
  - V1/
  - NaiveBayes_Model_V1/
✅ Training complete!
```

**Models created:**
- **IDF_V1**: TF-IDF feature transformer
- **V1**: Logistic Regression classifier (best performance)
- **NaiveBayes_Model_V1**: Naive Bayes classifier (backup)

### 7️⃣ Start Spark Streaming

```bash
python KafkaSpark-Streaming.py
```

**Expected output:**
```
Loading models...
Models loaded successfully.
🚀 Streaming started. Waiting for tweets...
```

### 8️⃣ Start Flask Web Application

Open a new terminal:
```bash
cd "Application - FLASK"
python main.py
```

Access the web app at: **http://127.0.0.1:5000**

***

## 🎮 Usage Guide

### Web Interface Features

#### 1. **Homepage** (`/`)
- **Manual Tweet Input**: Enter text and click "Post Tweet" for instant analysis
- **CSV Streaming**: Click "Start Stream" to auto-load tweets from validation dataset
- Real-time processing with live feedback

#### 2. **Live Stream Dashboard** (`/stream`)
- Real-time sentiment predictions displayed as cards
- Statistics counters (Total, Positive, Negative, Neutral)
- Confidence scores and latency metrics
- Auto-scrolling tweet feed

#### 3. **Results Table** (`/validation`)
- Historical predictions in sortable table format
- Sentiment badges with color coding
- Confidence percentages
- Export capabilities

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage with tweet input |
| `/stream` | GET | Live streaming dashboard |
| `/validation` | GET | Results table |
| `/produce_tweets` | POST | Submit tweet for analysis |
| `/stream_csv` | GET | Stream validation dataset |
| `/stream_inserts` | GET | Server-Sent Events (SSE) stream |

### Example: Submit Tweet via API

```bash
curl -X POST http://127.0.0.1:5000/produce_tweets \
  -H "Content-Type: application/json" \
  -d '{"tweetContent": "I love this product!"}'
```

**Response:**
```json
{
  "tweetContent": "I love this product!"
}
```

Check `/stream` to see the prediction!

***

## 🧠 Machine Learning Pipeline

### 1. **Data Preprocessing**
```python
Tokenizer → StopWordsRemover → HashingTF → IDF
```

- **Tokenization**: Split text into words
- **Stop Word Removal**: Remove common words (the, is, at, etc.)
- **HashingTF**: Convert words to feature vectors (8192 features)
- **IDF**: Weight features by importance

### 2. **Model Training**
```python
LogisticRegression(maxIter=100, regParam=0.01)
```

**Training Dataset**: 1.6M labeled tweets
- Negative: 0
- Positive: 1
- Neutral: 2
- Irrelevant: 3

**Performance Metrics:**
- Accuracy: **82%**
- Precision: **0.81**
- Recall: **0.80**
- F1-Score: **0.80**

### 3. **Real-Time Prediction**
```
Tweet → Preprocessing → Feature Extraction → Classification → MongoDB
```

**Average Latency:** 1-3 seconds per tweet

***

## 📊 Data Description

### Training Dataset (`X_training.csv`)
- **Size**: 1.6 million tweets
- **Columns**: 
  - `tweet_id`: Unique identifier
  - `entity`: Product/brand mentioned
  - `sentiment`: Label (Negative, Positive, Neutral, Irrelevant)
  - `content`: Tweet text

### Validation Dataset (`X_validation.csv`)
- **Size**: 500K tweets
- **Purpose**: Real-time streaming simulation
- **Format**: Same as training dataset

**Data Source**: [Kaggle - Twitter Entity Sentiment Analysis](https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis)

***

## 🛠️ Technologies Used

| Technology | Purpose | Version |
|------------|---------|---------|
| **Apache Kafka** | Message broker for streaming | 3.4.1 |
| **Apache Spark** | Distributed ML and streaming | 3.5.0 |
| **PySpark MLlib** | Machine learning library | 3.5.0 |
| **Flask** | Web framework | 3.0.0 |
| **MongoDB** | NoSQL database | 7.0 |
| **Python** | Primary language | 3.11 |
| **Docker** | Containerization | 24.0 |
| **JavaScript** | Frontend interactivity | ES6 |
| **HTML/CSS** | UI design | HTML5/CSS3 |

***

## 🐛 Troubleshooting

### Issue 1: Kafka Connection Error
```
org.apache.kafka.common.errors.TimeoutException
```

**Solution:**
```bash
# Check Kafka is running
docker ps | grep kafka

# Restart Kafka
docker-compose restart kafka
```

### Issue 2: Python Worker Timeout
```
Python worker failed to connect back
```

**Solution:**
Add to your script:
```python
os.environ['PYSPARK_PYTHON'] = 'path/to/python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'path/to/python.exe'
```

### Issue 3: MongoDB Connection Failed
```
ServerSelectionTimeoutError
```

**Solution:**
```bash
# Check MongoDB is running
mongosh --eval "db.version()"

# Start MongoDB
mongod --dbpath /path/to/data
```

### Issue 4: High Latency (>5 seconds)
**Solution:**
- Increase MongoDB connection pool: `maxPoolSize=50`
- Reduce batch interval: `processingTime='5 seconds'`
- Add indexes to MongoDB collection

***

## 📈 Performance Optimization

### Current Performance
- **Throughput**: 20-50 tweets/second
- **Latency**: 1-3 seconds per tweet
- **Model Accuracy**: 82%
- **MongoDB Insert Time**: 0.2-0.5 seconds

### Optimization Tips
1. **Increase Spark Partitions**: `spark.sql.shuffle.partitions=4`
2. **Enable Backpressure**: `spark.streaming.backpressure.enabled=true`
3. **Connection Pooling**: Use persistent MongoDB connections
4. **Batch Processing**: Group tweets in 5-second windows
5. **Model Caching**: Pre-load models to avoid repeated disk reads

***

## 🔮 Future Enhancements

- [ ] Twitter API v2 integration for live tweets
- [ ] Multi-language sentiment analysis
- [ ] Deep learning models (BERT, RoBERTa)
- [ ] Real-time dashboard analytics with charts
- [ ] User authentication and personalized feeds
- [ ] Sentiment trend analysis over time
- [ ] Export results to CSV/Excel
- [ ] Kubernetes deployment for scalability

***

## ✅ Testing / CI

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR to `main`. It does **not** spin up Kafka, Spark, or MongoDB - that requires live infrastructure this repo doesn't ship. Instead it checks that the code itself is sound:

- Installs all dependencies from `requirements.txt` (verifies they are resolvable/installable)
- Validates that every `.ipynb` notebook is structurally well-formed (via `nbformat`)
- Byte-compiles every `.py` script to catch syntax errors
- Runs `flake8` in two passes: a strict pass that fails the build on real errors (syntax errors, undefined names), and a lenient pass that reports style issues without failing the build

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

***

## 🙏 Acknowledgments

- [Kaggle](https://www.kaggle.com/) for the Twitter sentiment dataset
- [Apache Software Foundation](https://www.apache.org/) for Kafka and Spark
- [MongoDB Inc.](https://www.mongodb.com/) for the database
- [Flask Community](https://flask.palletsprojects.com/) for the web framework

***

## 📞 Contact

For questions or support, please open an issue on [GitHub](https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X/issues).

## 👤 Author

**Oussama EL HADJI** — [github.com/Bosaj](https://github.com/Bosaj)
(Team project — see contributors listed above.)

***

**⭐ Star this repository if you found it helpful!**

***

## 🚀 Quick Start (TL;DR)

```bash
# 1. Start Kafka
docker-compose up -d

# 2. Train models
cd Spark && python Spark-MLlib.py

# 3. Start streaming
python KafkaSpark-Streaming.py

# 4. Start web app (new terminal)
cd ../Application-FLASK && python main.py

# 5. Open browser
http://127.0.0.1:5000
```

**That's it! You're ready to analyze tweets in real-time! 🎉**


## 📊 Monitoring, Controlling, Evaluation & QA

This project includes a standardized 4-Pillar Observability and QA framework:
- **Logs & Prometheus/Grafana Monitoring**: Configured in `monitoring/` with Prometheus scraper configs and Grafana dashboards.
- **Health Controlling & Evaluation**: Liveness/readiness controllers in `monitoring/health.py` and evaluation harness in `scripts/eval_harness.py`.
- **QA & Testing**: Automated Pytest/Vitest integration and CI workflows via `.github/workflows/ci_qa_monitoring.yml`.

For complete instructions, architecture details, and commands, see [docs/MONITORING_AND_QA.md](file:///C:\Users\ROG FLOW\Desktop\Projects\Github_Projects\Real-Time_Sentiment_Analysis_on_X\docs\MONITORING_AND_QA.md).
