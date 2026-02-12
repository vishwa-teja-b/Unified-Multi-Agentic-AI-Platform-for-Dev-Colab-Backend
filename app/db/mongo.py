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

async def get_database():
    """
    Helper to get the database instance for background tasks.
    Assumes MONGO_URI and MONGODB_NAME are available in environment variables.
    """
    MONGO_URI = os.getenv("MONGODB_URL")
    MONGODB_NAME = os.getenv("MONGODB_DB_NAME")
    
    if not MONGO_URI or not MONGODB_NAME:
        raise ValueError("MONGODB_URL or MONGODB_DB_NAME not set in environment")

    client = AsyncMongoClient(MONGO_URI)
    return client[MONGODB_NAME]
