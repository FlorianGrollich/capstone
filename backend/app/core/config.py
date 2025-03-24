from typing import ClassVar

from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Wrong"
    mongo_url: str = "default url"
    jwt_secret_key: str = "default secret key"
    jwt_expire_minutes: int = 30
    jwt_algo: str = "HS256"
    model_config = SettingsConfigDict(env_file="../../.env")
    pwd_ctx: ClassVar[CryptContext] = CryptContext(schemes=["bcrypt"], deprecated="auto")


settings = Settings()
