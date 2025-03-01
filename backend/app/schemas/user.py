from typing import Optional

from pydantic import BaseModel, Field

from app.utils.types import PyObjectId


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
