from pymongo import MongoClient
import time

print("Testing Local MongoDB connection (localhost:27017)...")
try:
    client = MongoClient("mongodb://localhost:27017/?directConnection=true", serverSelectionTimeoutMS=2000)
    print(f"Is Primary: {client.is_primary}")
    client.admin.command('ping')
    print("✅ Local MongoDB is RUNNING and REACHABLE!")
except Exception as e:
    print(f"❌ Local MongoDB failed: {e}")
    
client.close()
