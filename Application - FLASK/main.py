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



# --- Configuration Management ---
# Default to Local
APP_CONFIG = {
    "db_type": "local",
    "cloud_uri": "",
    "groq_key": ""
}

def get_mongo_client(collection_name="TweetsPredictions", use_llm=False):
    col_name = "TweetsPredictionsLLM" if use_llm else "TweetsPredictions"
    
    if APP_CONFIG["db_type"] == "cloud" and APP_CONFIG["cloud_uri"]:
        uri = APP_CONFIG["cloud_uri"]
        # Use SSL for Cloud if needed
        return MongoClient(uri, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    else:
        # Default Local
        return MongoClient("mongodb://localhost:27017/?directConnection=true", serverSelectionTimeoutMS=2000)

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/settings", methods=['GET'])
def settings():
    return render_template('settings.html', 
                         current_db=APP_CONFIG["db_type"], 
                         cloud_uri=APP_CONFIG["cloud_uri"],
                         groq_key=APP_CONFIG["groq_key"])

@app.route("/update_settings", methods=['POST'])
def update_settings():
    APP_CONFIG["db_type"] = request.form.get("db_type", "local")
    APP_CONFIG["cloud_uri"] = request.form.get("cloud_uri", "")
    APP_CONFIG["groq_key"] = request.form.get("groq_key", "")
    
    # Save to .env logically if we wanted persistence, but for now runtime config + session
    
    return redirect('/settings')

@app.route("/stream", methods=['GET'])
def test():
    # Pass 'model_type' to template if we want to reuse streaming.html
    return render_template('streaming.html', model_type="Local Spark ML")

# New: LLM Stream Page
@app.route("/stream_llm", methods=['GET'])
def stream_llm_page():
    return render_template('streaming.html', model_type="Groq AI Analysis")

# Refactored Stream Endpoint (Generic)
def generic_stream_inserts(use_llm=False):
    def generate():
        client = get_mongo_client(use_llm=use_llm)
        db = client["BigData"]
        collection_name = "TweetsPredictionsLLM" if use_llm else "TweetsPredictions"
        collection = db[collection_name]
        
        last_id = None
        
        try:
            pipeline = [{'$match': {'operationType': 'insert'}}]
            change_stream = collection.watch(pipeline, max_await_time_ms=1000)
            print(f"✅ Change Stream ({collection_name}) connected.")
            
            for change in change_stream:
                data = change['fullDocument']
                if '_id' in data:
                    data['_id'] = str(data['_id'])
                if 'latency' not in data and 'created_at' in data:
                     data['latency'] = time.time() - data['created_at']
                yield f'data: {json.dumps(data)}\n\n'
                
        except Exception as e:
            print(f"⚠️ Stream ({collection_name}) failed: {e}. Switching to Polling.")
            while True:
                try:
                    query = {'_id': {'$gt': last_id}} if last_id else {}
                    docs = list(collection.find(query).sort('_id', -1).limit(10))
                    
                    if docs:
                        for doc in reversed(docs):
                            doc.pop('_id', None)
                            if 'latency' not in doc and 'created_at' in doc:
                                doc['latency'] = time.time() - doc['created_at']
                            yield f'data: {json.dumps(doc)}\n\n'
                        
                        if last_id is None:
                             last_id = docs[0].get('_id') # simple init
                        else:
                             # Update max seen
                             pass # Ideally track max id properly
                             
                    time.sleep(1.0)
                except Exception as poll_e:
                     print(f"Polling error: {poll_e}")
                     time.sleep(2.0)
        finally:
            client.close()

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

@app.route('/stream_inserts')
def stream_inserts():
    return generic_stream_inserts(use_llm=False)

@app.route('/stream_inserts_llm')
def stream_inserts_llm():
    return generic_stream_inserts(use_llm=True)


@app.route("/validation", methods=['GET'])
def validation():
    client = get_mongo_client()
    db = client["BigData"]
    collection = db["TweetsPredictions"]
    predictions = list(collection.find({}, {"_id": 0, "content": 1, "prediction": 1, "confidence": 1}).sort("_id", -1).limit(50))
    
    for p in predictions:
        val = p.get("prediction")
        mapped = map_prediction_to_sentiment(val)
        p["sentiment_label"] = mapped
    
    return render_template('validation.html', predictions=predictions)

@app.route('/produce_tweets', methods=['POST'])
def clear_tweets():
    data = request.json
    tweet_content = data['tweetContent']
    pattern = re.compile(r'[^\w\s.,!?;:\-\'"&()]')
    tweet_content = pattern.sub('', tweet_content)
    
    global producer
    if not producer:
        producer = get_kafka_producer()
    
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
            json_data = json.dumps({"content": row.iloc[3]})
            yield f"{json_data}\n"
            time.sleep(5)
    
    return Response(stream_with_context(generate()), mimetype='application/json')

if __name__ == "__main__":
    app.run()
