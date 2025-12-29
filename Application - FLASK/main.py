import os
import re
import time
from flask import Flask, jsonify, render_template, request, redirect, stream_with_context, Response
from kafka import KafkaProducer
import json
import pandas as pd
from pymongo import MongoClient
from bson.json_util import dumps
from dotenv import load_dotenv
import certifi

load_dotenv()

os.environ['PYTHONIOENCODING'] = 'utf-8'

app = Flask(__name__)
app.secret_key = 'TESTING' 
print("DEBUG: Loaded updated main.py v2") 

def get_kafka_producer():
    try:
        return KafkaProducer(bootstrap_servers=['localhost:9092'], 
                           value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                           request_timeout_ms=5000)
    except Exception as e:
        print(f"Warning: Kafka Producer connection failed: {e}")
        return None

producer = get_kafka_producer()

uri = os.getenv("MONGO_URI")

def watch_changes():
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client["BigData"]
    collection = db["TweetsPredictions"]
    change_stream = collection.watch([{'$match': {'operationType': 'insert'}}])
    for change in change_stream:
        yield 'data: {}\n\n'.format(dumps(change['fullDocument']))

def map_prediction_to_sentiment(prediction):
    try:
        # Handle floats (0.0) or strings ("0.0") by casting to int
        val = int(float(prediction))
    except (ValueError, TypeError):
        return 'Unknown'

    sentiments = {
        0: 'Negative',
        1: 'Positive',
        2: 'Neutral',
        3: 'Irrelevant'
    }
    return sentiments.get(val, 'Unknown')

@app.route('/stream_inserts')
def stream_inserts():
    def generate():
        for change in watch_changes():
            try:
                # Remove "data: " prefix if present and whitespace
                raw_data = change.replace("data: ", "").strip()
                if raw_data:
                    data = json.loads(raw_data)
                    import time
                    if 'created_at' in data:
                        data['latency'] = time.time() - data['created_at']
                    
                    prediction = data.get('prediction', 'Unknown')
                    mapped = map_prediction_to_sentiment(prediction)
                    data["sentiment_label"] = mapped
                    yield 'data: {}\n\n'.format(json.dumps(data))
            except Exception as e:
                print(f"Error in stream_inserts: {e}")
                
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

@app.route("/", methods = ['GET'])
def index():
    return render_template('index.html')

@app.route("/stream", methods=['GET'])
def test():
    return render_template('streaming.html')

@app.route("/validation", methods=['GET'])
def validation():
    client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = client["BigData"]
    collection = db["TweetsPredictions"]
    predictions = list(collection.find({}, {"_id": 0, "content": 1, "prediction": 1, "confidence": 1}).sort("_id", -1).limit(50))
    # Map predictions to labels
    for p in predictions:
        val = p.get("prediction")
        mapped = map_prediction_to_sentiment(val)
        print(f"DEBUG: Mapping {val} -> {mapped}")
        p["sentiment_label"] = mapped
    return render_template('validation.html', predictions=predictions)

@app.route('/produce_tweets', methods = ['POST'])
def clear_tweets():
    data = request.json
    tweet_content = data['tweetContent']
    pattern = re.compile(r'[^\w\s.,!?;:\-\'"&()]')
    tweet_content = pattern.sub('', tweet_content)
    print("Received tweet content:", tweet_content)
    global producer
    if not producer:
        producer = get_kafka_producer()
        
    import time
    if producer:
        message = {
            "content": tweet_content,
            "created_at": time.time()
        }
        producer.send('tweets', value=message)
    else:
        print("Kafka Producer not available, skipping message send.")
    return jsonify({"tweetContent": tweet_content})

@app.route('/stream_csv', methods=['GET'])
def stream_csv():
    def generate():
        data = pd.read_csv('../Spark/X_validation.csv', encoding='utf-8')
        for index, row in data.iterrows():
            json_data = json.dumps({"content": row[3]})
            yield f"{json_data}\n"
            time.sleep(5)  
            
    return Response(stream_with_context(generate()), mimetype='application/json')

if __name__ == "__main__":
    app.run()