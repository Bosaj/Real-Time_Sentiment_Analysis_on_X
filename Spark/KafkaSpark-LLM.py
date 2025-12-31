from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StringType, FloatType, StructType, StructField
from pymongo import MongoClient
import os
import requests
import json
import time
from dotenv import load_dotenv

# --- Environment Setup for Windows ---
os.environ['HADOOP_HOME'] = r"C:\Users\ROG FLOW\hadoop"
os.environ['hadoop.home.dir'] = r"C:\Users\ROG FLOW\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ['HADOOP_HOME'], 'bin')
os.environ['PYSPARK_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'), override=True)

# Config
GROQ_KEY_DEFAULT = os.getenv("GROQ_API_KEY", "") 
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions" # Correct Endpoint for Groq OpenAI-compatible
# Note: User provided code had "https://api.groq.com/v1/models/your-model/infer". 

spark = SparkSession.builder \
    .appName("SentimentAnalysisLLM") \
    .master("local[2]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Kafka Stream
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tweets") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

schema = StructType([
    StructField("content", StringType(), True),
    StructField("tracking_id", StringType(), True),
    StructField("created_at", FloatType(), True)
])

df = df.selectExpr("CAST(value AS STRING) as json_value")
df = df.select(from_json(col("json_value"), schema).alias("data")).select("data.*")
df = df.filter(col("content").isNotNull())

def llm_classify(text, api_key):
    if not api_key:
        return "Unknown", 0.0
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Analyze the sentiment of this tweet: "{text}"
    Classify strictly as one of: Positive, Negative, Neutral, Irrelevant.
    Return ONLY a JSON object: {{"sentiment": "Label", "confidence": 0.95}}
    """
    
    payload = {
        "model": "llama3-8b-8192", # Fast and cheap
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            # Parse JSON from content
            try:
                # Find JSON block if needed
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != -1:
                    parsed = json.loads(content[start:end])
                    return parsed.get("sentiment", "Unknown"), float(parsed.get("confidence", 0.0))
            except:
                pass
                
            # Fallback heuristic
            lower = content.lower()
            if "positive" in lower: return "Positive", 0.8
            if "negative" in lower: return "Negative", 0.8
            if "neutral" in lower: return "Neutral", 0.8
            if "irrelevant" in lower: return "Irrelevant", 0.8
            
    except Exception as e:
        print(f"LLM Error: {e}")
        
    return "Unknown", 0.0

def save_to_mongo(batch_df, batch_id):
    records = batch_df.collect()
    if not records:
        return
        
    print(f"📊 Processing Batch {batch_id} with LLM ({len(records)} tweets)...")
    
    # Connect Only When Needed
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/?directConnection=true")
    
    mongo_params = {
        "host": uri,
        "serverSelectionTimeoutMS": 2000,
        "connectTimeoutMS": 2000,
        "socketTimeoutMS": 2000,
    }
    
    import certifi # Ensure imported if not at top, but usually is. 
    # Actually certifi is not imported in LLM script yet? Let's check imports.
    # checking imports: "import certifi" WAS NOT in previous view of LLM script?
    # I need to add import certifi at top first? 
    # The tool only replaces this block. 
    # Let's assume I need to add import. 
    # Wait, I cannot add import at top with this replace block.
    # I will stick to basic replace here, and add import in separate call if needed.
    # Or I can import inline:
    
    if "mongodb+srv" in uri:
        import certifi
        mongo_params["tlsCAFile"] = certifi.where()
        mongo_params["tlsAllowInvalidCertificates"] = True
        
    mongo_client = MongoClient(**mongo_params)
    db = mongo_client["BigData"]
    collection = db["TweetsPredictionsLLM"]
    
    groq_key = os.getenv("GROQ_API_KEY", GROQ_KEY_DEFAULT)
    
    final_docs = []
    
    for row in records:
        sentiment, confidence = llm_classify(row.content, groq_key)
        
        doc = {
            "content": row.content,
            "prediction": sentiment, # String for LLM
            "sentiment_label": sentiment,
            "confidence": confidence,
            "created_at": row.created_at,
            "model": "Groq-LLM",
            "tracking_id": row.tracking_id if hasattr(row, 'tracking_id') else None
        }
        final_docs.append(doc)
        print(f"   🤖 {sentiment}: {row.content[:50]}...")
        
    if final_docs:
        collection.insert_many(final_docs)
    
    mongo_client.close()

query = df.writeStream \
    .foreachBatch(save_to_mongo) \
    .trigger(processingTime='10 seconds') \
    .start()

print("🚀 LLM Streaming started. Waiting for tweets...")
query.awaitTermination()
