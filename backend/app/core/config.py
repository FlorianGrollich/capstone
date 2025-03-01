from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Wrong"
    mongo_url: str = "default url"
    model_config = SettingsConfigDict(env_file="../../.env")



settings = Settings()