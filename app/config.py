from pydantic_settings import BaseSettings
import logging

class Settings(BaseSettings):
    openai_api_key: str
    redis_host: str
    redis_port: int
    redis_db: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int

    class Config:
        env_file = ".env"

logging.basicConfig(level=logging.INFO)
settings = Settings()