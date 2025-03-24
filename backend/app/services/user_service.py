from typing import Optional

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas.token import TokenData
from app.schemas.user import UserModel
from app.utils.authentication import create_jwt


class UserService:
    def __init__(self, user_collection: AsyncIOMotorCollection):
        self.collection = user_collection

    async def register(self, user: UserModel) -> UserModel:
        """
        creates one user document in Mongo Collection and checks if write operation was successful and returns JWT

        :param user:
        :return user:
        """
        user = user.model_dump()
        result = await self.collection.insert_one(user)
        created_user = await self.collection.find_one({"_id": result.inserted_id})

        if created_user is None:
            raise HTTPException(status_code=500, detail="User was not created successfully")

        return create_jwt(UserModel(**created_user))

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
