from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas.user import UserModel


class UserService:
    def __init__(self, user_collection: AsyncIOMotorCollection):
        self.collection = user_collection

    async def create_user(self, user: UserModel) -> UserModel:
        """
        creates one user document in Mongo Collection and checks if write operation was successful

        :param user:
        :return user:
        """
        user = user.model_dump()
        result = await self.collection.insert_one(user)
        created_user = await self.collection.find_one({"_id": result.inserted_id})

        if created_user is None:
            raise HTTPException(status_code=500, detail="User was not created successfully")

        return UserModel(**created_user)


