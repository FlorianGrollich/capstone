from motor.motor_asyncio import AsyncIOMotorClient

from capstone.backend.app.core.config import settings

client = AsyncIOMotorClient(settings.mongo_url)
db = client.test

def get_mongo_collection(collection_name: str):
    return db[collection_name]