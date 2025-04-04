from datetime import datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings
from app.schemas.token import TokenData
from app.schemas.user import UserModel


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return settings.pwd_ctx.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return settings.pwd_ctx.hash(password)


def create_jwt(user: UserModel):
    to_encode = TokenData(email=user.email, )
    current_time = datetime.now()
    if settings.jwt_expire_minutes is not None:
        expire = current_time + timedelta(minutes=settings.jwt_expire_minutes)
    else:
        expire = current_time + timedelta(minutes=15)
    to_encode.exp = expire
    encoded_jwt = jwt.encode(to_encode.model_dump(), settings.jwt_secret_key, algorithm=settings.jwt_algo)
    return encoded_jwt


def decode_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algo])
        return payload
    except jwt.PyJWTError:
        return None
