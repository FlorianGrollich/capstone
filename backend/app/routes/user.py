from fastapi import APIRouter
from fastapi.params import Depends

from app.core.depedencies import get_user_service
from app.schemas.user import UserModel
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register")
async def create_user(
        user: UserModel,
        user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user)
