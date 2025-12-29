from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.ml.classification import LogisticRegression, NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .master("local[*]") \
    .getOrCreate()

schema = StructType([
    StructField("TweetID", IntegerType(), True),
    StructField("Entity", StringType(), True),
    StructField("Sentiment", StringType(), True),
    StructField("Content", StringType(), True)
])

df = spark.read.csv("X_training.csv", header=False, schema=schema)
df = df.filter(df["Content"].isNotNull())

tokenizer = Tokenizer(inputCol="Content", outputCol="words")
df_words = tokenizer.transform(df)

remover = StopWordsRemover(inputCol="words", outputCol="filtered")
df_filtered = remover.transform(df_words)

hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
featurizedData = hashingTF.transform(df_filtered)
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)
idfModel.write().overwrite().save("IDF_V1")

indexer = StringIndexer(inputCol="Sentiment", outputCol="label")
indexer_model = indexer.fit(rescaledData)
df_final = indexer_model.transform(rescaledData)

train_data, test_data = df_final.randomSplit([0.8, 0.2], seed=1234)

lr = LogisticRegression(featuresCol='features', labelCol='label')
paramGrid_lr = (ParamGridBuilder()
             .addGrid(lr.regParam, [0.1, 0.01])  
             .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0]) 
             .addGrid(lr.maxIter, [10, 50, 100]) 
             .build())
evaluator_lr = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
crossval_lr = CrossValidator(estimator=lr,
                          estimatorParamMaps=paramGrid_lr,
                          evaluator=evaluator_lr,
                          numFolds=3)  
cvModel_lr = crossval_lr.fit(train_data)
predictions_lr = cvModel_lr.transform(test_data)
accuracy_lr = evaluator_lr.evaluate(predictions_lr)
print("Logistic Regression Accuracy: %f" % accuracy_lr)
bestModel_lr = cvModel_lr.bestModel
print("Best model parameters for Logistic Regression:")
print("regParam:", bestModel_lr._java_obj.getRegParam())
print("elasticNetParam:", bestModel_lr._java_obj.getElasticNetParam())
print("maxIter:", bestModel_lr._java_obj.getMaxIter())

nb = NaiveBayes(featuresCol='features', labelCol='label')
paramGrid_nb = (ParamGridBuilder()
             .addGrid(nb.smoothing, [0.0, 1.0, 2.0])  
             .build())
evaluator_nb = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
crossval_nb = CrossValidator(estimator=nb,
                          estimatorParamMaps=paramGrid_nb,
                          evaluator=evaluator_nb,
                          numFolds=3)  
cvModel_nb = crossval_nb.fit(train_data)
predictions_nb = cvModel_nb.transform(test_data)
accuracy_nb = evaluator_nb.evaluate(predictions_nb)
print("Naive Bayes Classifier Accuracy: %f" % accuracy_nb)
bestModel_nb = cvModel_nb.bestModel
print("Best model parameters for Naive Bayes:")
print("Smoothing parameter:", bestModel_nb._java_obj.getSmoothing())

with open("sentiment_to_index_mapping.txt", "w") as file:
    labels_to_index = indexer_model.labels
    for index, label in enumerate(labels_to_index):
        file.write(f"Numeric index {index} corresponds to Sentiment: '{label}'\n")

bestModel_lr.write().overwrite().save("V1")
cvModel_nb.write().overwrite().save("NaiveBayes_Model_V1")

predictions_lr.select("Content", "label", "prediction").show()

spark.stop()
