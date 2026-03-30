import os
from urllib.parse import parse_qsl, urlsplit, urlunsplit
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from app.core.config import settings
from typing import AsyncGenerator
import asyncio
import logging

# Prevent libpq-style env vars from leaking into asyncpg
for key in ("PGSSLMODE", "PGCHANNELBINDING", "PGSSLROOTCERT", "PGSSLCERT", "PGSSLKEY", "PGSSLCRL"):
    os.environ.pop(key, None)

def _sanitize_db_url(url: str) -> tuple[str, bool]:
    if url.startswith("sqlite"):
        return url, False
    parts = urlsplit(url)
    raw_pairs = parse_qsl(parts.query, keep_blank_values=True)
    cleaned_pairs = []
    ssl_required = False
    for key, value in raw_pairs:
        key_clean = key.strip().lower()
        value_clean = value.strip().strip("\"'")
        if key_clean in {"sslmode", "channel_binding", "sslrootcert", "sslcert", "sslkey", "sslcrl"}:
            if key_clean == "sslmode" and value_clean in {"require", "verify-full", "verify-ca"}:
                ssl_required = True
            continue
        if key_clean == "ssl" and value_clean.lower() in {"true", "1", "yes"}:
            ssl_required = True
            continue
        cleaned_pairs.append((key.strip(), value_clean))

    # Neon requires SSL; avoid passing sslmode to asyncpg
    if "neon.tech" in (parts.netloc or ""):
        ssl_required = True

    # Drop all query params to avoid asyncpg parsing libpq options
    sanitized = urlunsplit((parts.scheme, parts.netloc, parts.path, "", parts.fragment))
    return sanitized, ssl_required

# Use SQLModel engines for compatibility
db_url, ssl_required = _sanitize_db_url(settings.DATABASE_URL)
connect_args = {"ssl": True} if ssl_required else {}
engine = create_async_engine(db_url, echo=True, future=True, connect_args=connect_args)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

logger = logging.getLogger(__name__)

async def init_db():
    """
    Initializes the database connection and runs migrations.
    In production, this replaces manual 'create_all' with Alembic versioning.
    """
    retries = 15
    delay = 4
    for i in range(retries):
        try:
            # Check connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                
                # Check for advisory lock to prevent multiple workers from migrating at once
                if engine.dialect.name == "postgresql":
                    await conn.execute(text("SELECT pg_advisory_xact_lock(42)"))
                
                logger.info("Database connection established. Running migrations...")
                
                # Run Alembic migrations programmatically
                # Note: This runs in the same thread, which is fine for startup
                from alembic.config import Config
                from alembic import command
                
                def run_upgrade():
                    alembic_cfg = Config("alembic.ini")
                    # Enforce the same DATABASE_URL from settings
                    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
                    command.upgrade(alembic_cfg, "head")

                # Alembic's 'upgrade' command is synchronous, but our env.py handles the async loop
                # So we just call it.
                await asyncio.to_thread(run_upgrade)

            logger.info("Database initialized and migrated successfully.")
            return
        except Exception as e:
            if i < retries - 1:
                logger.warning(f"Database initialization failed (attempt {i+1}/{retries}): {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Database initialization failed after {retries} attempts. Exiting.")
                raise e
