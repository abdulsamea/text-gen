# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
