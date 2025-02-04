from pydantic_settings import BaseSettings
import logging

class Settings(BaseSettings):
    openai_api_key: str
    redis_host: str
    redis_port: int
    redis_db: int

    class Config:
        env_file = ".env"

logging.basicConfig(level=logging.INFO)
settings = Settings()