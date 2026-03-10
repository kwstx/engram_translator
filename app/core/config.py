from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
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
    
    DATABASE_URL: Optional[str] = None

    # Task queue (SQL-backed)
    TASK_POLL_INTERVAL_SECONDS: float = 2.0
    TASK_LEASE_SECONDS: int = 60
    TASK_MAX_ATTEMPTS: int = 5
    AGENT_MESSAGE_LEASE_SECONDS: int = 60
    AGENT_MESSAGE_MAX_ATTEMPTS: int = 5

    # Auth
    AUTH_ISSUER: str = "https://auth.example.com/"
    AUTH_AUDIENCE: str = "translator-middleware"
    AUTH_JWT_ALGORITHM: str = "HS256"
    AUTH_JWT_SECRET: Optional[str] = None
    AUTH_JWT_PUBLIC_KEY: Optional[str] = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _finalize_database_url(self):
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )
        elif self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = "postgresql+asyncpg://" + self.DATABASE_URL[len("postgres://") :]
        elif (
            self.DATABASE_URL.startswith("postgresql://")
            and "+asyncpg" not in self.DATABASE_URL
        ):
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self

settings = Settings()
