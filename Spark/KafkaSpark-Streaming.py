import os
import sys
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, current_timestamp
from pyspark.sql.types import StringType, DoubleType, StructType, StructField
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml.feature import IDFModel, Tokenizer, StopWordsRemover, HashingTF
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# --- Environment Setup (Crucial for Windows) ---
os.environ['HADOOP_HOME'] = r"C:\Users\ROG FLOW\hadoop"
os.environ['hadoop.home.dir'] = r"C:\Users\ROG FLOW\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ['HADOOP_HOME'], 'bin')
os.environ['PYSPARK_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'

load_dotenv()

# --- Optimized SparkSession ---
spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.driver.host", "127.0.0.1") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.streaming.kafka.maxRatePerPartition", "50") \
    .config("spark.streaming.backpressure.enabled", "true") \
    .config("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", "false") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("Loading models...")
try:
    idfModel = IDFModel.load("IDF_V1")
    lrModel = LogisticRegressionModel.load("V1")
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    sys.exit(1)

# --- Read from Kafka ---
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tweets") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .option("maxOffsetsPerTrigger", "50") \
    .load()

# --- Parse JSON ---
json_schema = StructType([
    StructField("content", StringType(), True),
    StructField("created_at", DoubleType(), True)
])

df = df.selectExpr("CAST(value AS STRING) as json_value")
df = df.select(from_json(col("json_value"), json_schema).alias("data")).select("data.*")
df = df.filter(col("content").isNotNull())

# --- Apply ML Pipeline ---
tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=8192)

df = tokenizer.transform(df)
df = remover.transform(df)
df = hashingTF.transform(df)
df = idfModel.transform(df)
df = lrModel.transform(df)

# Add processing timestamp
df = df.withColumn("processed_at", current_timestamp())

# Extract confidence
def get_confidence(probability):
    if probability:
        return float(max(probability))
    return 0.0

confidence_udf = udf(get_confidence, DoubleType())
df = df.withColumn("confidence", confidence_udf(col("probability")))

# --- MongoDB Connection Pool ---
uri = os.getenv("MONGO_URI")
_mongo_client = None

def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(
            uri,
            tlsCAFile=certifi.where(),
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=45000,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
    return _mongo_client

def save_to_mongo(batch_df, batch_id):
    start_time = time.time()
    
    try:
        if batch_df.isEmpty():
            return
        
        # Select required columns and collect
        rows = batch_df.select("content", "prediction", "confidence", "created_at").collect()
        
        if not rows:
            return
        
        # Map predictions
        sentiment_map = {0: 'Negative', 1: 'Positive', 2: 'Neutral', 3: 'Irrelevant'}
        
        records = []
        for row in rows:
            # Calculate latency if created_at exists
            latency = 0.0
            if row.created_at:
                latency = time.time() - float(row.created_at)
            
            records.append({
                "content": row.content,
                "prediction": int(row.prediction),
                "sentiment_label": sentiment_map.get(int(row.prediction), 'Unknown'),
                "confidence": float(row.confidence),
                "created_at": row.created_at,
                "latency": latency
            })
        
        # Use persistent connection pool
        client = get_mongo_client()
        db = client["BigData"]
        collection = db["TweetsPredictions"]
        
        # Bulk insert (unordered for speed)
        collection.insert_many(records, ordered=False)
        
        elapsed = time.time() - start_time
        print(f"✅ Batch {batch_id}: {len(records)} records | MongoDB time: {elapsed:.3f}s")
        
        # Print sample for debug
        # if len(records) > 0:
        #    print(f"   Sample: {records[0]['sentiment_label']} (Latency: {records[0]['latency']:.2f}s)")
        
    except Exception as e:
        print(f"❌ Batch {batch_id} error: {str(e)}")

# --- Start Streaming ---
query = df.writeStream \
    .trigger(processingTime='5 seconds') \
    .foreachBatch(save_to_mongo) \
    .outputMode("append") \
    .option("checkpointLocation", "./checkpoint") \
    .start()

print("🚀 Streaming started. Waiting for data...")
query.awaitTermination()
