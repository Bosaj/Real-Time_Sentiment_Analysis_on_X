from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDFModel
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.sql.functions import col, from_json, udf, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import certifi
import ssl
import os
from dotenv import load_dotenv
import time
import sys

# --- Environment Setup for Windows ---
os.environ['HADOOP_HOME'] = r"C:\Users\ROG FLOW\hadoop"
os.environ['hadoop.home.dir'] = r"C:\Users\ROG FLOW\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ['HADOOP_HOME'], 'bin')
os.environ['PYSPARK_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'

load_dotenv()

# Ultra-optimized SparkSession
spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .master("local[2]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.port", "40400") \
    .config("spark.blockManager.port", "40401") \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.streaming.kafka.maxRatePerPartition", "20") \
    .config("spark.streaming.backpressure.enabled", "true") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("Loading models...")
try:
    idfModel = IDFModel.load("IDF_V1")
    lrModel = LogisticRegressionModel.load("V1")
    print("Models loaded successfully.\n")
except Exception as e:
    print(f"Error loading models: {e}")
    sys.exit(1)

# Kafka stream
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tweets") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .option("maxOffsetsPerTrigger", "20") \
    .load()

# Parse JSON
schema = StructType([
    StructField("content", StringType(), True),
    StructField("created_at", DoubleType(), True)
])

df = df.selectExpr("CAST(value AS STRING) as json_value")
df = df.select(from_json(col("json_value"), schema).alias("data")).select("data.*")
df = df.filter(col("content").isNotNull())

# ML Pipeline
tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=8192)

df = tokenizer.transform(df)
df = remover.transform(df)
df = hashingTF.transform(df)
df = idfModel.transform(df)
df = lrModel.transform(df)

# Extract confidence
def get_confidence(probability):
    if probability:
        return float(max(probability))
    return 0.0

confidence_udf = udf(get_confidence, DoubleType())
df = df.withColumn("confidence", confidence_udf(col("probability")))
df = df.select("content", "prediction", "confidence", "created_at")

# MongoDB connection - SWITCHED TO LOCAL FOR PERFORMANCE & RELIABILITY
uri = "mongodb://localhost:27017/?directConnection=true"
print(f"📡 MongoDB URI: {uri} (Local)\n")

# Local Connection (No SSL needed)
mongo_client = MongoClient(
    uri,
    maxPoolSize=100,
    minPoolSize=20,
    maxIdleTimeMS=60000,
    serverSelectionTimeoutMS=2000,
    connectTimeoutMS=2000,
    socketTimeoutMS=2000,
    retryWrites=True,
    w=0 
)

db = mongo_client["BigData"]
collection = db["TweetsPredictions"]

# Test connection
try:
    mongo_client.admin.command('ping')
    print("✅ MongoDB connection successful!\n")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}\n")

# Ensure indexes exist
try:
    collection.create_index("created_at", background=True)
    collection.create_index("sentiment_label", background=True)
    print("✅ Indexes created\n")
except:
    pass

def save_to_mongo(batch_df, batch_id):
    batch_start = time.time()
    
    try:
        if batch_df.isEmpty():
            return
        
        rows = batch_df.collect()
        
        if not rows:
            return
        
        sentiment_map = {0: 'Negative', 1: 'Positive', 2: 'Neutral', 3: 'Irrelevant'}
        
        records = []
        current_time = time.time()
        
        for row in rows:
            latency = 0.0
            if row.created_at:
                latency = current_time - float(row.created_at)
                
            records.append({
                "content": row.content,
                "prediction": int(row.prediction),
                "sentiment_label": sentiment_map.get(int(row.prediction), 'Unknown'),
                "confidence": round(float(row.confidence), 2),
                "created_at": row.created_at,
                "latency": round(latency, 3)
            })
        
        # MongoDB insert
        mongo_start = time.time()
        try:
            collection.insert_many(records, ordered=False)
        except BulkWriteError as e:
            print(f"⚠️ Partial write: {len(e.details.get('writeErrors', []))} errors")
        except Exception as e:
            print(f"⚠️ Write warning: {str(e)[:100]}")
        
        mongo_time = time.time() - mongo_start
        total_time = time.time() - batch_start
        
        # Print results
        print(f"\n{'='*90}")
        print(f"📊 BATCH {batch_id} | Records: {len(records)} | Total: {total_time:.2f}s | MongoDB: {mongo_time:.3f}s")
        print(f"{'='*90}")
        
        for record in records[:5]:
            sentiment = record['sentiment_label']
            confidence = record['confidence']
            latency = record['latency']
            content = record['content'][:70]
            
            icon = {'Positive': '✅', 'Negative': '❌', 'Neutral': '⚪', 'Irrelevant': '🔵'}.get(sentiment, '❔')
            print(f"{icon} {sentiment:12} | Conf: {confidence:.2f} | Latency: {latency:.2f}s")
            # print(f"   💬 {content}...")
        
        if len(records) > 5:
            print(f"   ... and {len(records) - 5} more tweets")
        
        print(f"{'='*90}\n")
        
    except Exception as e:
        print(f"\n❌ Batch {batch_id} ERROR: {str(e)}")

# Start streaming
query = df.writeStream \
    .trigger(processingTime='3 seconds') \
    .foreachBatch(save_to_mongo) \
    .outputMode("append") \
    .option("checkpointLocation", "./checkpoint") \
    .start()

print("🚀 Streaming started. Waiting for tweets...\n")
query.awaitTermination()
