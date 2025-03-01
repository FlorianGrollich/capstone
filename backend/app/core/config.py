from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Wrong"
    model_config = SettingsConfigDict(env_file="../../.env")



s = Settings()
print(s.app_name)

