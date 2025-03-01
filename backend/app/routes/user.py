from fastapi import APIRouter
from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.depedencies import get_user_collection

router = APIRouter()


@router.post("/create-user")
async def create_user(user_collection: AsyncIOMotorCollection = Depends(get_user_collection())):
    pass
