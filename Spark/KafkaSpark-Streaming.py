from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StringType, FloatType, StructType, StructField
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml.feature import IDFModel, Tokenizer, StopWordsRemover, HashingTF
from pymongo import MongoClient

spark = SparkSession.builder \
    .appName("RealTimeTweetProcessing") \
    .master("local[*]") \
    .getOrCreate()

model = LogisticRegressionModel.load("V1")
idfModel = IDFModel.load("IDF_V1")

schema = StructType([StructField("STRING", StringType(), True)])

client = MongoClient("mongodb://localhost:27017/BigData")
db = client["BigData"]
collection = db["TweetsPredictions"]

def max_probability(prob):
    return float(max(prob))

get_max_prob = udf(max_probability, FloatType())

tweets_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tweets") \
    .load() \
    .selectExpr("CAST(value AS STRING)")

tweets_df.writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

tweets_df = tweets_df \
    .select(col("value").alias("content"))

tweets_df.writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")

featurized_data = hashingTF.transform(remover.transform(tokenizer.transform(tweets_df)))

featurized_data.writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

rescaled_data = idfModel.transform(featurized_data)

rescaled_data.writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

predictions = model.transform(rescaled_data)
predictions = predictions.withColumn("confidence", get_max_prob(predictions["probability"]))

predictions.writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

predictions_to_save = predictions.select("content", "prediction", "confidence")

def save_to_mongo(batch_df, batch_id):
    print(f"Processing batch {batch_id}")
    batch_df.show(truncate=False)  
    records = batch_df.toPandas().to_dict("records")
    if records:
        print(f"Inserting {len(records)} records to MongoDB")
        collection.insert_many(records)
    else:
        print("No records to insert for this batch")

query = predictions_to_save.writeStream \
    .foreachBatch(save_to_mongo) \
    .outputMode("append") \
    .start()

query.awaitTermination()
