import csv
import json
import time
from kafka import KafkaProducer

def main():
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    csv_file = 'X_validation.csv'
    print(f"Streaming data from {csv_file} to Kafka topic 'tweets'...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # Row format in validation: TweetID, Entity, Sentiment, Content
            if len(row) < 4:
                continue
            
            content = row[3]
            # Send just the content as the consumer expects
            # Consumer expects: json.loads(x.decode('utf-8')) -> string content?
            # Wait, Spark/Kafka-Streaming.py: tweet_content = message.value
            # If we send plain string or JSON?
            # Consumer deserializer: lambda x: json.loads(x.decode('utf-8'))
            # So we must send a JSON string that *evaluates* to the content string?
            # OR, does the consumer expect a JSON object?
            # Spark/Kafka-Streaming.py line 45: df = spark.createDataFrame([(tweet_content,)], schema=schema)
            # Schema is "content": StringType.
            # So if message.value is "Hello", df is [("Hello")].
            
            # However, json.loads("Hello") fails. json.loads('"Hello"') works.
            # So if producer sends json.dumps("Hello"), the wire has "Hello" (quotes included).
            # Consumer does json.loads -> "Hello". Correct.
            
            producer.send('tweets', value=content)
            print(f"Sent: {content}")
            time.sleep(1) # Simulate real-time streaming

    print("Finished streaming.")

if __name__ == "__main__":
    main()
