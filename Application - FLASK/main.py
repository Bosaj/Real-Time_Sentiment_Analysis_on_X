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

# Load environment variables from the root .env file, overriding any stale system envs
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'), override=True)
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
    if "mongodb+srv" in uri:
        client = MongoClient(uri, tlsCAFile=certifi.where())
    else:
        client = MongoClient(uri)
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
# Initialize from Env (persisted state) or Default to Local
APP_CONFIG = {
    "db_type": "cloud" if "mongodb+srv" in os.getenv("MONGO_URI", "") else "local",
    "cloud_uri": os.getenv("MONGO_URI", "") if "mongodb+srv" in os.getenv("MONGO_URI", "") else "",
    "groq_key": os.getenv("GROQ_API_KEY", "")
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
    return render_template('index.html', config=APP_CONFIG)

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
                # tracking_id is already in fullDocument if inserted by Spark
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



# --- Configuration Routes ---
@app.route("/advanced-settings")
def advanced_settings():
    return render_template("advanced_settings.html", config=APP_CONFIG)

@app.route("/mongodb-config", methods=['GET', 'POST'])
def mongodb_config():
    if request.method == 'POST':
        db_type = request.form.get("db_type")
        cloud_uri = request.form.get("cloud_uri", "")
        APP_CONFIG["db_type"] = db_type
        APP_CONFIG["cloud_uri"] = cloud_uri
        save_to_env()
        return redirect('/advanced-settings')
        
    return render_template("mongodb_config.html", 
                         db_type=APP_CONFIG.get("db_type", "local"),
                         cloud_uri=APP_CONFIG.get("cloud_uri", ""))

@app.route("/ai-config", methods=['GET', 'POST'])
def ai_config():
    if request.method == 'POST':
        model_type = request.form.get("model_type")
        groq_key = request.form.get("groq_key", "")
        APP_CONFIG["model_type"] = model_type
        APP_CONFIG["groq_key"] = groq_key
        save_to_env()
        return redirect('/advanced-settings')
        
    return render_template("ai_config.html", 
                         model_type=APP_CONFIG.get("model_type", "spark"),
                         groq_key=APP_CONFIG.get("groq_key", ""))

@app.route("/update_kafka_settings", methods=['POST'])
def update_kafka_settings():
    # Placeholder for future implementation
    return redirect('/advanced-settings')

def save_to_env():
    """Helper to persist APP_CONFIG to .env"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Spark', '.env')
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
    try:
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
        
        new_lines = []
        keys_updated = {'GROQ_API_KEY': False, 'MONGO_URI': False}
        
        for line in lines:
            if line.startswith('GROQ_API_KEY=') and 'groq_key' in APP_CONFIG:
                new_lines.append(f'GROQ_API_KEY="{APP_CONFIG["groq_key"]}"\n')
                keys_updated['GROQ_API_KEY'] = True
            elif line.startswith('MONGO_URI=') and 'db_type' in APP_CONFIG:
                uri_val = APP_CONFIG["cloud_uri"] if APP_CONFIG["db_type"] == 'cloud' else "mongodb://localhost:27017/?directConnection=true"
                new_lines.append(f'MONGO_URI="{uri_val}"\n')
                keys_updated['MONGO_URI'] = True
            else:
                new_lines.append(line)
        
        if not keys_updated['GROQ_API_KEY'] and 'groq_key' in APP_CONFIG:
            new_lines.append(f'\nGROQ_API_KEY="{APP_CONFIG["groq_key"]}"\n')
            
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
            
    except Exception as e:
        print(f"⚠️ Failed to save .env: {e}")

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
def produce_tweets():
    data = request.json
    tweet_content = data.get('tweetContent')
    tracking_id = data.get('tracking_id')
    
    if not tweet_content:
        return jsonify({"error": "No content provided"}), 400

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
        if tracking_id:
            message["tracking_id"] = tracking_id
            
        producer.send('tweets', value=message)
        print(f"Produced: {tweet_content[:20]}... ID: {tracking_id}")
    else:
        print("Kafka Producer not available, skipping message send.")
    
    return jsonify({
        "status": "queued",
        "tweetContent": tweet_content, 
        "tracking_id": tracking_id
    })

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
