from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Wrong"
    mongo_url: str = "default url"
    jwt_secret_key: str = "default secret key"
    model_config = SettingsConfigDict(env_file="../../.env")
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()