from dotenv import load_dotenv
import os
from pymongo import MongoClient, DESCENDING
from datetime import datetime



load_dotenv()




def get_mongo_db():
    mongo_url = os.getenv("MONGODB_URI", "")
    client = MongoClient(mongo_url)
    return client.get_database("guardianai")


def get_latest_last_scan(wallet_address):
    db = get_mongo_db()
    collection = db["wallets"]

    latest_document = collection.find_one(
        {"wallet": wallet_address},
        projection={"response.last_scan": 1, "_id": 0},
        sort=[("timestamp", DESCENDING)]
    )
    return latest_document["response"]["last_scan"] if latest_document else None




def save_response_to_database(wallet, response_data):
    db = get_mongo_db()
    response = convert_large_integers(response_data)
    response["timestamp"] = datetime.utcnow()
    document = {
        "wallet": wallet,
        "timestamp": response["timestamp"],
        "response": response
    }
    db.wallets.insert_one(document)

def convert_large_integers(data):
    if isinstance(data, dict):
        return {key: convert_large_integers(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_large_integers(item) for item in data]
    elif isinstance(data, int) and data > 2147483647:
        return 2147483647
    else:
        return data
