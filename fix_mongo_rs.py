from pymongo import MongoClient
from pymongo.errors import OperationFailure

uri = "mongodb://localhost:27017/?directConnection=true"
client = MongoClient(uri, serverSelectionTimeoutMS=2000)

print("Attempting to fix Local MongoDB Replica Set...")

try:
    # Check status
    try:
        status = client.admin.command("replSetGetStatus")
        print(f"Current Status: {status.get('myState')}")
        # State 1 is Primary, 2 is Secondary, 0 is Startup, 6 is Unknown, 10 is Removed?
    except OperationFailure as e:
        print(f"Status check failed (expected if not initialized): {e}")

    # Attempt Initiate
    try:
        config = {
            "_id": "rs0", # Default name, or try to guess? 
            # If we don't know the name, initiate() with no args might work if fresh.
            "members": [{"_id": 0, "host": "localhost:27017"}]
        }
        # First try raw initiate (fresh start)
        client.admin.command("replSetInitiate")
        print("✅ replSetInitiate SUCCESS! Node should become Primary.")
    except OperationFailure as e:
        print(f"replSetInitiate failed: {e}")
        if "already initialized" in str(e):
             # Maybe reconfig?
             pass

except Exception as e:
    print(f"❌ Error: {e}")

client.close()
