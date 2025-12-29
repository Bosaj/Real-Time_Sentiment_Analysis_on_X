import sys
import os
from dotenv import load_dotenv

load_dotenv()

print(f"Python sys.path: {sys.path}")
print(f"Java Home: {os.environ.get('JAVA_HOME')}")
print(f"Spark Home: {os.environ.get('SPARK_HOME')}")

try:
    from pyspark.sql import SparkSession
    print("PySpark imported successfully.")
    
    spark = SparkSession.builder \
        .appName("VerifySpark") \
        .master("local[*]") \
        .getOrCreate()
        
    print(f"Spark Session created. Version: {spark.version}")
    
    data = [("Java", 20000), ("Python", 100000), ("Scala", 3000)]
    df = spark.createDataFrame(data, ["Language", "Users"])
    print("DataFrame created successfully.")
    df.show()
    
    spark.stop()
    print("Spark verification complete.")
    
except ImportError as e:
    print(f"Error importing PySpark: {e}")
except Exception as e:
    print(f"An error occurred during verification: {e}")
