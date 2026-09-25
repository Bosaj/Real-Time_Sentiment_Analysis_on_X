import os
import sys

import certifi
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient

# Load environment variables
load_dotenv()
uri = os.getenv("MONGO_URI")

if not uri:
    print("Error: MONGO_URI not found in environment variables.")
    sys.exit(1)

print("Connecting to MongoDB...")
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["BigData"]
collection = db["TweetsPredictions"]

print("Creating indexes...")
# Create indexes for faster queries
# created_at DESC for latest tweets
collection.create_index([("created_at", DESCENDING)])
# sentiment_label for stats
collection.create_index([("sentiment_label", ASCENDING)])
# content for potential lookups
collection.create_index([("content", ASCENDING)])

print("✅ Indexes created successfully!")
client.close()
