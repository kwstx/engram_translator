from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, AmqpDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agent Translator Middleware"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    HTTPS_ONLY: bool = False
    LOG_LEVEL: str = "INFO"
    
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

    # Auth
    AUTH_ISSUER: str = "https://auth.example.com/"
    AUTH_AUDIENCE: str = "translator-middleware"
    AUTH_JWT_ALGORITHM: str = "HS256"
    AUTH_JWT_SECRET: Optional[str] = None
    AUTH_JWT_PUBLIC_KEY: Optional[str] = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
