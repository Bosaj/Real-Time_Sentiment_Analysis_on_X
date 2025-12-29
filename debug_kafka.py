from kafka import KafkaConsumer
import json

try:
    print("Connecting to Kafka...")
    consumer = KafkaConsumer(
        'tweets',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        consumer_timeout_ms=5000,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    print("Connected. Listening for messages...")
    count = 0
    for message in consumer:
        print(f"Received: {message.value}")
        count += 1
        if count >= 5:
            break
            
    if count == 0:
        print("No messages found in 'tweets' topic.")
    else:
        print(f"Successfully consumed {count} messages.")
        
except Exception as e:
    print(f"Error consuming from Kafka: {e}")
