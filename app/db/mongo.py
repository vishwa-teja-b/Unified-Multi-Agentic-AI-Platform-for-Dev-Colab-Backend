from pymongo import AsyncMongoClient
from pymongo import ReturnDocument
from dotenv import load_dotenv
import os

load_dotenv()

# MONGO_URI = os.getenv("MONGODB_URL")

def create_mongo_client(MONGO_URI: str):
    
    client = AsyncMongoClient(MONGO_URI)

    print("✅ MongoDB connected successfully")

    return client
