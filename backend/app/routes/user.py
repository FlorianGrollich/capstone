from fastapi import APIRouter
from fastapi.params import Depends

from capstone.backend.app.core.dependencies import get_user_service
from capstone.backend.app.schemas.user import AuthenticationDTO
from capstone.backend.app.services.user_service import UserService

router = APIRouter()


@router.post("/register")
async def register(
        user: AuthenticationDTO,
        user_service: UserService = Depends(get_user_service)):
    return await user_service.register(user)


@router.post("/login")
async def login(
        user: AuthenticationDTO,
        user_service: UserService = Depends(get_user_service)):
    return await user_service.login(user)
