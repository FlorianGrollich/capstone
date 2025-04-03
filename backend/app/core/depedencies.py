from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.database import get_mongo_collection
from app.services.user_service import UserService
from app.core.config import settings
from app.services.video_service import VideoService


def get_settings():
    return settings


def get_user_collection() -> AsyncIOMotorCollection:
    return get_mongo_collection("user")


def get_user_service(user_collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> UserService:
    return UserService(user_collection)


def get_video_service() -> VideoService:
    return VideoService()
