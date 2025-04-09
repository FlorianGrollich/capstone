from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorCollection
from starlette import status

from app.core.database import get_mongo_collection
from app.services.user_service import UserService
from app.core.config import settings
from app.services.video_service import VideoService
from app.utils.authentication import decode_jwt


def get_settings():
    return settings


def get_user_collection() -> AsyncIOMotorCollection:
    return get_mongo_collection("user")

def get_video_collection() -> AsyncIOMotorCollection:
    return get_mongo_collection("video")


def get_user_service(user_collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> UserService:
    return UserService(user_collection)


def get_video_service(user_collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> VideoService:
    return VideoService(user_collection)


security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = decode_jwt(credentials.credentials)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
