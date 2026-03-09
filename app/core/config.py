from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, AmqpDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agent Translator Middleware"
    API_V1_STR: str = "/api/v1"
    
    # Postgres
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "translator_db"
    
    @computed_field
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # RabbitMQ
    RABBITMQ_USER: str = "user"
    RABBIT_PASSWORD: str = "password"
    RABBIT_HOST: str = "rabbitmq"
    RABBIT_PORT: int = 5672
    
    @computed_field
    def RABBIT_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
