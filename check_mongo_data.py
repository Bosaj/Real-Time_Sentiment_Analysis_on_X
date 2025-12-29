from pymongo import MongoClient
import time
import os
from dotenv import load_dotenv

load_dotenv()

import certifi

try:
    client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = client["BigData"]
    collection = db["TweetsPredictions"]
    
    count = collection.count_documents({})
    print(f"Total documents in collection: {count}")
    
    if count > 0:
        print("Last 5 documents:")
        for doc in collection.find().sort("_id", -1).limit(5):
            print(doc)
    else:
        print("Collection is empty.")
        
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
