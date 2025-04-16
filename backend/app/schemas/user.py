from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict

from capstone.backend.app.utils.types import PyObjectId


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    password: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )


class AuthenticationDTO(BaseModel):
    email: str
    password: str
