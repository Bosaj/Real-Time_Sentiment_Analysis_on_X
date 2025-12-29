# Real-Time Sentiment Analysis on Twitter Streams

## Project Creators
- ELHADJI Oussama
- BEN ACHA Yassine
- CHAKOR Abdellatif
- MENACH Achraf

## Overview
This project develops a web application for real-time sentiment analysis of Twitter streams using Apache Kafka and machine learning models. The application categorizes each tweet as Negative, Positive, Neutral, or Irrelevant.

## Multimedia Content
- **Video Demonstration**

  [Link to Video Demonstration](https://github.com/OmarNouih/Twitter-Streams/assets/27814897/04f5149b-f44d-4218-b10e-1583bfb92ee7)

## Architecture
- **APP**: Flask application, static resources, and HTML templates.
- **Spark**: Machine learning and stream processing scripts, datasets.

## Setup Instructions

### Docker Setup for Kafka
To get Kafka running via Docker, execute the following commands:
```bash
cd path_to_project_directory
docker-compose up -d
```

### Building the Spark-Jupyter Docker Image
Build the Docker image using the Dockerfile provided:
```bash
docker build -t spark-jupyter:latest .
```

### Docker Container for Spark
Run the Docker container, ensuring to mount the Spark directory so that it is accessible within the container:
```bash
docker run -p 8888:8888 -v path_to_your_project_directory/Spark:/home/jovyan/work spark-jupyter:latest
```
This mounts the `Spark` directory to `/home/jovyan/work` within the Jupyter environment.

### Training the Sentiment Analysis Model
Navigate to the Spark directory and execute the training script:
```bash
spark-submit Spark-MLlib.py
```

### Streaming with Kafka
Start the Kafka streaming process with the following command:
```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2,org.mongodb.spark:mongo-spark-connector_2.12:3.0.0 KafkaSpark-Streaming.py
```
or

```bash
spark-submit Kafka-Streaming.py
```
### MongoDB Setup
Ensure MongoDB is operational and the URI is set up as per your `main.py` , `Kafka-Streaming.py` configuration.

## Flask Application Usage
- `/stream_inserts`: Endpoint for real-time stream inserts.
- `/`: Homepage and stream testing.
- `/stream`: Stream simulation interface.
- `/validation`: Model validation and predictions display.
- `/produce_tweets`: Processes and queues tweets for analysis.
- `/stream_csv`: Streams validation data for real-time analysis.

## Data Description
The training dataset `X_training.csv` includes tweets with their sentiment labels. The `X_validation.csv` dataset contains tweets used for real-time sentiment prediction.

## Tools and Frameworks
The project utilizes Apache Kafka Stream, Spark MLlib, NLTK, Pandas, Matplotlib, Flask, and Django. It is developed in Python with supplementary use of Java and JavaScript.

## Data Source
Twitter Entity Sentiment Analysis data obtained from [Kaggle](https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis).

## Testing Streams
There are two ways to test the streams within the application:
1. Real-time text entry for immediate sentiment analysis.
2. Use the "Start Streaming Tweets" button to initiate streaming from `X_validation.csv`. 

## File Descriptions

1. **KafkaSpark-Streaming.py**: This script utilizes Spark Structured Streaming to consume tweets from Kafka, perform sentiment analysis using a pre-trained machine learning model, and save the results to MongoDB.

    - **Structured Streaming with Kafka**: The script sets up a structured streaming process to consume real-time tweets from Kafka topics. It integrates Kafka as a source for streaming data, leveraging Spark's structured streaming API for real-time data processing.
    
    - **Sentiment Analysis**: After consuming tweets, the script applies sentiment analysis using a pre-trained machine learning model. It tokenizes, preprocesses, and transforms the tweets into feature vectors before making sentiment predictions.
    
    - **MongoDB Integration**: Results from the sentiment analysis are then stored in MongoDB for further analysis or retrieval by downstream applications.

2. **KafkaProducer-Streaming.py**: This script collects tweets in real-time using the Twitter API and produces them to a Kafka topic for further processing.

    - **Producer-Consumer Architecture**: The script serves as a Kafka producer, continuously fetching tweets from the Twitter API and publishing them to a specified Kafka topic. It follows the producer-consumer pattern, where it acts as a data source for downstream consumers, such as the KafkaSpark-Streaming.py script.
    
    - **Real-Time Data Collection**: Utilizing the Twitter API, the script collects tweets in real-time, ensuring a continuous stream of data for downstream processing.

## Project Repository
The source code is available at _[[GitHub repository link](https://github.com/Bosaj/Real-Time_Sentiment_Analysis_on_X)]_.
