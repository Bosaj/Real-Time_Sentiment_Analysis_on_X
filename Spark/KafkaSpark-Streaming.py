import os
import sys
os.environ['HADOOP_HOME'] = r"C:\Users\ROG FLOW\hadoop"
os.environ['hadoop.home.dir'] = r"C:\Users\ROG FLOW\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ['HADOOP_HOME'], 'bin')
os.environ['PYSPARK_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\ROGFLO~1\AppData\Local\Programs\Python\PYTHON~3\python.exe'

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StringType, FloatType, StructType, StructField, IntegerType
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StringType, FloatType, StructType, StructField, IntegerType
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml.feature import IDFModel, Tokenizer, StopWordsRemover, HashingTF, StringIndexer
from pymongo import MongoClient
import hashlib
from pymongo.errors import PyMongoError, DuplicateKeyError
from dotenv import load_dotenv
import certifi

load_dotenv()

spark = SparkSession.builder \
    .appName("RealTimeTweetProcessing") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.driver.host", "127.0.0.1") \
    .master("local[*]") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "20") \
    .config("spark.default.parallelism", "20") \
    .config("spark.python.worker.timeout", "600") \
    .config("spark.network.timeout", "600s") \
    .config("spark.driver.maxResultSize", "4g") \
    .getOrCreate()

# --- Load Models ---
print("Loading models...")
try:
    idfModel = IDFModel.load("IDF_V1")
    model = LogisticRegressionModel.load("V1")
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    # Fallback or exit? For now, we assume models exist
    raise e

# --- Streaming Phase ---
schema = StructType([StructField("STRING", StringType(), True)])

client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client["BigData"]
collection = db["TweetsPredictions"]

def max_probability(prob):
    return float(max(prob))

get_max_prob = udf(max_probability, FloatType())

tweets_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tweets") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING)")

from pyspark.sql.types import DoubleType
json_schema = StructType([
    StructField("content", StringType(), True),
    StructField("created_at", DoubleType(), True)
])

tweets_df = tweets_df.withColumn("data", from_json(col("value"), json_schema)).select("data.*")
tweets_df = tweets_df.filter(col("content").isNotNull())

tweets_df.writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

# tweets_df = tweets_df.select(col("value").alias("content")) - Handled by JSON parsing

tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=8192)

featurized_data = hashingTF.transform(remover.transform(tokenizer.transform(tweets_df)))

rescaled_data = idfModel.transform(featurized_data)

predictions = model.transform(rescaled_data)
predictions = predictions.withColumn("confidence", get_max_prob(predictions["probability"]))

# predictions.writeStream \
#     .format("console") \
#     .option("truncate", False) \
#     .start()

# UDF to generate deterministic ID
import time

# UDF to generate deterministic ID (with timestamp to allow re-sending same content)
def generate_id(content):
    if content is None:
        return None
    # Add timestamp to make ID unique per submission instance
    unique_str = content + str(time.time())
    return hashlib.md5(unique_str.encode('utf-8')).hexdigest()

generate_id_udf = udf(generate_id, StringType())

# Add _id for deduplication
predictions = predictions.withColumn("_id", generate_id_udf(col("content")))

predictions_to_save = predictions.select("content", "prediction", "confidence", "_id", "created_at")

def save_to_mongo(batch_df, batch_id):
    print(f"DEBUG: Processing batch {batch_id}")
    try:
        # Convert to Pandas for batch insert
        pandas_df = batch_df.toPandas()
        
        if len(pandas_df) > 0:
            print(f"DEBUG: Inserting {len(pandas_df)} records to MongoDB...")
            # Re-instantiate client to be safe with timeouts
            local_client = MongoClient(os.getenv("MONGO_URI"), 
                                     tlsCAFile=certifi.where(),
                                     serverSelectionTimeoutMS=5000,
                                     connectTimeoutMS=10000)
            local_db = local_client["BigData"]
            local_collection = local_db["TweetsPredictions"]
            
            records = pandas_df.to_dict("records")
            try:
                # ordered=False continues to insert other docs if one fails (e.g. duplicate)
                local_collection.insert_many(records, ordered=False)
            except DuplicateKeyError:
                pass # Expected for duplicates
            except PyMongoError as e:
                # Check for bulk write error which might contain duplicates
                if "E11000" in str(e):
                    pass
                else:
                    print(f"MongoDB Bulk Write Error in {batch_id}: {e}")
            
            print("DEBUG: Insertion complete.")
            local_client.close()
        else:
            print("DEBUG: Batch is empty.")
            
    except PyMongoError as e:
        print(f"MongoDB Error in batch {batch_id}: {str(e)}")
    except Exception as e:
        print(f"ERROR in save_to_mongo batch {batch_id}: {str(e)}")

query = predictions_to_save.writeStream \
    .foreachBatch(save_to_mongo) \
    .trigger(processingTime='2 seconds') \
    .outputMode("append") \
    .start()

query.awaitTermination()
