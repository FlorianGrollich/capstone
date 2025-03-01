from app.core.database import get_mongo_collection
from config import settings


def get_settings():
    return settings


def get_user_collection():
    return get_mongo_collection("user")
