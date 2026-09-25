import json
import os

from kafka import KafkaConsumer
from pymongo import MongoClient
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml.feature import IDFModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType, StringType, StructField, StructType

spark = SparkSession.builder.appName("RealTimeTweetProcessing").master("local[*]").getOrCreate()

model = LogisticRegressionModel.load("V1")
idfModel = IDFModel.load("IDF_V1")

schema = StructType([StructField("content", StringType(), True)])

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
db = client["BigData"]
collection = db["TweetsPredictions"]

consumer = KafkaConsumer(
    "tweets",
    bootstrap_servers=["kafka:29092"],
    enable_auto_commit=False,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)


def max_probability(prob):
    return float(max(prob))


get_max_prob = udf(max_probability, FloatType())

print("Starting Kafka consumer...")
for message in consumer:
    try:
        tweet_content = message.value
        if tweet_content:
            print(f"Received tweet: {tweet_content}")
            df = spark.createDataFrame([(tweet_content,)], schema=schema)
            from pyspark.ml.feature import HashingTF, StopWordsRemover, Tokenizer

            tokenizer = Tokenizer(inputCol="content", outputCol="words")
            remover = StopWordsRemover(inputCol="words", outputCol="filtered")
            hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
            featurized_data = hashingTF.transform(remover.transform(tokenizer.transform(df)))
            rescaled_data = idfModel.transform(featurized_data)
            predictions = model.transform(rescaled_data)
            predictions = predictions.withColumn("confidence", get_max_prob(predictions["probability"]))
            predictions_to_save = predictions.select("content", "prediction", "confidence").collect()
            for row in predictions_to_save:
                record = {
                    "content": row["content"],
                    "prediction": int(row["prediction"]),
                    "confidence": float(row["confidence"]),
                }
                print(
                    f"Received tweet : {tweet_content}, prediction : {int(row['prediction'])}, confidence : {float(row['confidence'])}"
                )
                collection.insert_one(record)
    except Exception as e:
        print(f"Error processing message: {e}")
spark.stop()
print("Kafka consumer closed.")
