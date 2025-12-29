from pymongo import MongoClient
import os
import certifi
from dotenv import load_dotenv

load_dotenv()
try:
    client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = client["BigData"]
    collection = db["TweetsPredictions"]
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} documents. Collection is clean.")
except Exception as e:
    print(f"Error: {e}")
