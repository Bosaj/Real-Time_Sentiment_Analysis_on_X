from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDFModel
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import certifi
import os
from dotenv import load_dotenv
import time
import sys
import signal
import atexit
from datetime import datetime
from collections import defaultdict
import warnings
import io
import contextlib

# === SUPPRESS ALL WARNINGS AND ERRORS ===
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['PYSPARK_SUBMIT_ARGS'] = '--conf spark.ui.showConsoleProgress=false pyspark-shell'

import logging
logging.getLogger("py4j").setLevel(logging.FATAL)
logging.getLogger("pyspark").setLevel(logging.FATAL)
logging.getLogger("org.apache.spark").setLevel(logging.FATAL)

# === ENVIRONMENT SETUP ===
os.environ['HADOOP_HOME'] = r"C:\Users\ROG FLOW\hadoop"
os.environ['hadoop.home.dir'] = r"C:\Users\ROG FLOW\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ['HADOOP_HOME'], 'bin')
os.environ['PYSPARK_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'), override=True)

# === COLORS ===
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

USE_COLORS = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

def colored(text, color_code):
    return f"{color_code}{text}{Colors.ENDC}" if USE_COLORS else text

def print_header(text):
    print(colored(f"\n{'='*100}", Colors.OKCYAN))
    print(colored(f"  {text}", Colors.BOLD))
    print(colored(f"{'='*100}\n", Colors.OKCYAN))

def print_section(text):
    print(colored(f"\n{'─'*100}", Colors.OKBLUE))
    print(colored(f"  {text}", Colors.OKBLUE))
    print(colored(f"{'─'*100}", Colors.OKBLUE))

# === SESSION STATS ===
class SessionStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_batches = 0
        self.total_tweets = 0
        self.sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0, 'Irrelevant': 0}
        self.total_processing_time = 0
        self.total_mongo_time = 0
        self.avg_latency = []

stats = SessionStats()

# === SPARK SESSION ===
print_header("🚀 SPARK SENTIMENT ANALYSIS STREAMING")
print(colored("⚙️  Initializing Spark Session...", Colors.OKCYAN))

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
    .config("spark.ui.showConsoleProgress", "false") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print(colored("✅ Spark Session Started", Colors.OKGREEN))

# === GRACEFUL SHUTDOWN ===
query_obj = None
shutdown_requested = False

def graceful_shutdown(signum=None, frame=None):
    global shutdown_requested, query_obj
    
    if shutdown_requested:
        return
    shutdown_requested = True
    
    print(colored("\n\n⏹️  Stopping stream gracefully...", Colors.WARNING))
    
    # Suppress all stderr output during shutdown
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            if query_obj is not None:
                query_obj.stop()
                print(colored("  ✅ Stream stopped", Colors.OKGREEN))
        except:
            print(colored("  ✅ Stream stopped", Colors.OKGREEN))
    
    print_summary_stats()
    
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            if spark is not None:
                spark.stop()
                print(colored("  ✅ Spark session stopped", Colors.OKGREEN))
        except:
            print(colored("  ✅ Spark session stopped", Colors.OKGREEN))
    
    print_header("👋 SESSION ENDED")
    os._exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)
atexit.register(graceful_shutdown)

# === LOAD MODELS ===
print_section("📦 Loading ML Models")
try:
    idfModel = IDFModel.load("IDF_V1")
    lrModel = LogisticRegressionModel.load("V1")
    print(colored("  ✅ Models Loaded Successfully", Colors.OKGREEN))
except Exception as e:
    print(colored(f"  ❌ Error loading models: {e}", Colors.FAIL))
    sys.exit(1)

# === KAFKA STREAM ===
print_section("📡 Connecting to Kafka")
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tweets") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .option("maxOffsetsPerTrigger", "20") \
    .load()

print(colored("  ✅ Kafka Stream Connected (localhost:9092 → tweets)", Colors.OKGREEN))

# === PARSE JSON ===
schema = StructType([
    StructField("content", StringType(), True),
    StructField("tracking_id", StringType(), True),
    StructField("created_at", DoubleType(), True)
])

df = df.selectExpr("CAST(value AS STRING) as json_value")
df = df.select(from_json(col("json_value"), schema).alias("data")).select("data.*")
df = df.filter(col("content").isNotNull())

# === ML PIPELINE ===
print_section("🤖 Building ML Pipeline")

tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=8192)

df = tokenizer.transform(df)
df = remover.transform(df)
df = hashingTF.transform(df)
df = idfModel.transform(df)
df = lrModel.transform(df)

def get_confidence(probability):
    if probability:
        return float(max(probability))
    return 0.0

confidence_udf = udf(get_confidence, DoubleType())
df = df.withColumn("confidence", confidence_udf(col("probability")))
df = df.select("content", "prediction", "confidence", "created_at", "tracking_id")

print(colored("  ✅ Pipeline: Tokenize → StopWords → HashTF → IDF → LogisticRegression", Colors.OKGREEN))

# === MONGODB ===
print_section("🗄️  Connecting to MongoDB")
uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/?directConnection=true")

mongo_type = "Cloud (Atlas)" if "mongodb+srv" in uri else "Local"
mongo_display = uri.split('@')[1] if '@' in uri else uri.replace('mongodb://', '').replace('mongodb+srv://', '')
print(colored(f"  📍 Type: {mongo_type}", Colors.OKCYAN))
print(colored(f"  🔗 URI:  {mongo_display}", Colors.OKCYAN))

mongo_params = {
    "host": uri,
    "maxPoolSize": 100,
    "minPoolSize": 20,
    "maxIdleTimeMS": 60000,
    "serverSelectionTimeoutMS": 2000,
    "connectTimeoutMS": 2000,
    "socketTimeoutMS": 2000,
    "retryWrites": True,
    "w": 0 
}

if "mongodb+srv" in uri:
    mongo_params["tlsCAFile"] = certifi.where()
    mongo_params["tlsAllowInvalidCertificates"] = True

mongo_client = MongoClient(**mongo_params)
db = mongo_client["BigData"]
collection = db["TweetsPredictions"]

try:
    mongo_client.admin.command('ping')
    print(colored(f"  ✅ MongoDB Connected", Colors.OKGREEN))
    collection.create_index("created_at", background=True)
    collection.create_index("sentiment_label", background=True)
    print(colored(f"  ✅ Indexes Created", Colors.OKGREEN))
except Exception as e:
    print(colored(f"  ⚠️  MongoDB: {e}", Colors.WARNING))

# === STATS FUNCTION ===
def print_summary_stats():
    elapsed = time.time() - stats.start_time
    avg_batch_time = stats.total_processing_time / stats.total_batches if stats.total_batches > 0 else 0
    avg_mongo_time = stats.total_mongo_time / stats.total_batches if stats.total_batches > 0 else 0
    avg_latency = sum(stats.avg_latency) / len(stats.avg_latency) if stats.avg_latency else 0
    tweets_per_sec = stats.total_tweets / elapsed if elapsed > 0 else 0
    
    print_section("📊 SESSION STATISTICS")
    print(f"  ⏱️  Runtime:          {elapsed:.1f}s")
    print(f"  📦 Total Batches:    {stats.total_batches}")
    print(f"  💬 Total Tweets:     {stats.total_tweets}")
    print(f"  ⚡ Tweets/Second:    {tweets_per_sec:.2f}")
    print(f"  ⏱️  Avg Batch Time:   {avg_batch_time:.2f}s")
    print(f"  🗄️  Avg MongoDB Time: {avg_mongo_time:.3f}s")
    print(f"  ⌛ Avg Latency:      {avg_latency:.2f}s")
    print(f"\n  📈 Sentiment Distribution:")
    for sentiment, count in stats.sentiment_counts.items():
        percentage = (count / stats.total_tweets * 100) if stats.total_tweets > 0 else 0
        icon = {'Positive': '✅', 'Negative': '❌', 'Neutral': '⚪', 'Irrelevant': '🔵'}[sentiment]
        print(f"     {icon} {sentiment:12} {count:4} ({percentage:5.1f}%)")

# === BATCH PROCESSOR ===
def save_to_mongo(batch_df, batch_id):
    if shutdown_requested or batch_df.isEmpty():
        return
    
    batch_start = time.time()
    
    try:
        rows = batch_df.collect()
        if not rows:
            return
        
        stats.total_batches += 1
        stats.total_tweets += len(rows)
        
        sentiment_map = {0: 'Negative', 1: 'Positive', 2: 'Neutral', 3: 'Irrelevant'}
        records = []
        current_time = time.time()
        batch_sentiments = defaultdict(int)
        
        for row in rows:
            latency = current_time - float(row.created_at) if row.created_at else 0.0
            stats.avg_latency.append(latency)
            sentiment = sentiment_map.get(int(row.prediction), 'Unknown')
            stats.sentiment_counts[sentiment] += 1
            batch_sentiments[sentiment] += 1
                
            records.append({
                "content": row.content,
                "prediction": int(row.prediction),
                "sentiment_label": sentiment,
                "confidence": round(float(row.confidence), 2),
                "created_at": row.created_at,
                "latency": round(latency, 3),
                "tracking_id": row.tracking_id if hasattr(row, 'tracking_id') else None
            })
        
        # MongoDB insert
        mongo_start = time.time()
        try:
            collection.insert_many(records, ordered=False)
        except:
            pass
        
        mongo_time = time.time() - mongo_start
        total_time = time.time() - batch_start
        
        stats.total_processing_time += total_time
        stats.total_mongo_time += mongo_time
        
        # Output
        timestamp = datetime.now().strftime("%H:%M:%S")
        sentiment_summary = " | ".join([f"{k[:3]}:{v}" for k, v in batch_sentiments.items()])
        
        print(f"\n[{timestamp}] Batch #{batch_id:3d} │ Tweets: {len(records):2d} │ {sentiment_summary} │ "
              f"Time: {total_time:.2f}s │ DB: {mongo_time:.3f}s")
        
        for i, record in enumerate(records[:3]):
            sentiment = record['sentiment_label']
            confidence = record['confidence']
            latency = record['latency']
            content = record['content'][:75]
            icon = {'Positive': '✅', 'Negative': '❌', 'Neutral': '⚪', 'Irrelevant': '🔵'}.get(sentiment, '❔')
            print(f"  {i+1}. {icon} {sentiment:11} │ {confidence:.2f} │ {latency:.2f}s │ {content}...")
        
        if len(records) > 3:
            print(f"     ... +{len(records) - 3} more")
        
        if stats.total_batches % 20 == 0:
            print_summary_stats()
        
    except Exception as e:
        if not shutdown_requested:
            print(colored(f"❌ Batch {batch_id} ERROR: {str(e)}", Colors.FAIL))

# === START STREAMING ===
print_header("🎬 STARTING LIVE STREAMING")
print(colored(f"  📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.OKCYAN))
print(colored(f"  🔄 Batch Interval: 3 seconds", Colors.OKCYAN))
print(colored(f"  💡 Press Ctrl+C to stop\n", Colors.WARNING))

query_obj = df.writeStream \
    .trigger(processingTime='3 seconds') \
    .foreachBatch(save_to_mongo) \
    .outputMode("append") \
    .option("checkpointLocation", "./checkpoint") \
    .start()

try:
    query_obj.awaitTermination()
except KeyboardInterrupt:
    graceful_shutdown()
except:
    graceful_shutdown()
