from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.database import get_mongo_collection
from app.services.user_service import UserService
from config import settings


def get_settings():
    return settings


def get_user_collection() -> AsyncIOMotorCollection:
    return get_mongo_collection("user")


def get_user_service(user_collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> UserService:
    return UserService(user_collection)
