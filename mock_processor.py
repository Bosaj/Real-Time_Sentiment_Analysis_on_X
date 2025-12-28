import json
import random
from kafka import KafkaConsumer
from pymongo import MongoClient

def get_sentiment(text):
    text = text.lower()
    
    # Negative phrases
    negative_keywords = ['bad', 'hate', 'worst', 'sad', 'awful', 'terrible', 'get lost', 'fail', 'stupid', 'idiot', 'useless', 'bug', 'error', 'broken', 'slow']
    if any(word in text for word in negative_keywords):
        return "Negative"

    # Positive phrases
    positive_keywords = ['good', 'great', 'love', 'best', 'happy', 'cool', 'awesome', 'amazing', 'win', 'success', 'fixed', 'works', 'nice', 'thank']
    if any(word in text for word in positive_keywords):
        return "Positive"

    # Neutral phrases
    neutral_keywords = ['ok', 'fine', 'meh', 'average', 'normal', 'check', 'testing']
    if any(word in text for word in neutral_keywords):
        return "Neutral"

    return "Irrelevant" # Default fallback

def main():
    print("Starting Mock Tweet Processor...")
    
    try:
        # Connect to Kafka
        consumer = KafkaConsumer(
            'tweets',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            value_deserializer=lambda x: x.decode('utf-8')
        )
        print("Connected to Kafka. Waiting for tweets...")

        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/BigData")
        db = client["BigData"]
        collection = db["TweetsPredictions"]
        print("Connected to MongoDB.")

        for message in consumer:
            content = message.value
            print(f"Received tweet: {content}")
            
            # Simulate processing
            prediction = get_sentiment(content)
            confidence = round(random.uniform(0.75, 0.99), 2)
            
            # Main app expects: content, prediction (int), confidence
            record = {
                "content": content,
                "prediction": prediction,
                "confidence": confidence
            }
            
            result = collection.insert_one(record)
            print(f"Saved prediction: {prediction} (Confidence: {confidence}) - ID: {result.inserted_id}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
