import os
import time

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

print(f"Testing MongoDB connection: {uri[:40]}...")

# Test connection speed
start = time.time()
client = MongoClient(
    uri,
    tlsCAFile=certifi.where() if "mongodb+srv" in uri else None,
    serverSelectionTimeoutMS=5000,
)

# Try a simple operation
db = client["BigData"]
collection = db["TweetsPredictions"]

# Insert test
test_data = {"test": "performance", "timestamp": time.time()}
insert_start = time.time()
collection.insert_one(test_data)
insert_time = time.time() - insert_start

# Query test
query_start = time.time()
result = collection.find_one({"test": "performance"})
query_time = time.time() - query_start

# Cleanup
collection.delete_one({"test": "performance"})

total_time = time.time() - start

print("\n📊 Results:")
print(f"   Connection time: {total_time:.3f}s")
print(f"   Insert time: {insert_time:.3f}s")
print(f"   Query time: {query_time:.3f}s")

if "mongodb+srv" in uri:
    print("\n⚠️  WARNING: You're using MongoDB Atlas (cloud)")
    print("   Network latency is adding 2-5 seconds per operation")
    print("   Recommendation: Use local MongoDB for development")
else:
    print("\n✅ Using local MongoDB or explicit URI")

if insert_time > 0.5:
    print(f"\n❌ Insert is SLOW ({insert_time:.3f}s)")
    print("   Expected: <0.1s for local, <0.5s for Atlas")
else:
    print(f"\n✅ Insert is FAST ({insert_time:.3f}s)")

client.close()
