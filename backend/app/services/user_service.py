from typing import Optional

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from capstone.backend.app.schemas.user import UserModel, AuthenticationDTO
from capstone.backend.app.utils.authentication import create_jwt, get_password_hash, verify_password


class UserService:
    def __init__(self, user_collection: AsyncIOMotorCollection):
        self.collection = user_collection

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """
        finds user by email if no user is found return None
        :param email:
        :return user | None:
        """
        user = await self.collection.find_one({"email": email})

        if user is None:
            return None

        return UserModel(**user)

    async def register(self, user: AuthenticationDTO) -> str:
        """
        creates one user document in Mongo Collection and checks if write operation was successful and returns JWT

        :param user:
        :return jwt:
        """

        existing_user = await self.get_user_by_email(user.email)
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Email already exists")

        user.password = get_password_hash(user.password)
        user = user.model_dump()
        result = await self.collection.insert_one(user)
        created_user = await self.collection.find_one({"_id": result.inserted_id})

        if created_user is None:
            raise HTTPException(status_code=500, detail="User was not created successfully")

        return create_jwt(UserModel(**created_user))


    async def login(self, user: AuthenticationDTO) -> str:
        """
        check if credentials are correct and if are correct return jwt

        :param user:
        :return jwt:
        """

        existing_user = await self.get_user_by_email(user.email)
        if existing_user is None:
            raise HTTPException(status_code=400, detail="Email or Password is not correct!")

        if verify_password(user.password, existing_user.password) is False:
            raise HTTPException(status_code=400, detail="Email or Password is not correct!")

        return create_jwt(existing_user)



