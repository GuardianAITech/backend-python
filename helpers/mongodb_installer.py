from dotenv import load_dotenv
import os
from pymongo import MongoClient

def prepare_mongodb():
    
    mongodb_uri = os.getenv("MONGODB_URI", "")
    client = MongoClient(mongodb_uri)

    database_name = "guardianai"
    collection_name = "wallets"

    if database_name not in client.list_database_names():
        db = client[database_name]
    else:
        db = client.get_database(database_name)
    
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
    else:
        print(f"Using existing collection '{collection_name}'.")


