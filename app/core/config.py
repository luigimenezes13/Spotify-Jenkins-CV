from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    node_env: str = "development"
    port: int = 3000
    host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
