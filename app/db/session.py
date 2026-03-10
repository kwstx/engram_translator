import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from app.core.config import settings
from typing import AsyncGenerator

# Prevent libpq-style env vars from leaking into asyncpg
for key in ("PGSSLMODE", "PGCHANNELBINDING", "PGSSLROOTCERT", "PGSSLCERT", "PGSSLKEY", "PGSSLCRL"):
    os.environ.pop(key, None)

def _sanitize_db_url(url: str) -> str:
    parts = urlsplit(url)
    raw_pairs = parse_qsl(parts.query, keep_blank_values=True)
    cleaned_pairs = []
    for key, value in raw_pairs:
        key_clean = key.strip().lower()
        if key_clean in {"sslmode", "channel_binding", "sslrootcert", "sslcert", "sslkey", "sslcrl"}:
            continue
        cleaned_pairs.append((key.strip(), value.strip().strip("\"'")))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(cleaned_pairs), parts.fragment))

# Use SQLModel engines for compatibility
engine = create_async_engine(_sanitize_db_url(settings.DATABASE_URL), echo=True, future=True)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        # Import models here to make sure they are registered with SQLModel.metadata
        from app.db.models import (
            ProtocolMapping,
            ProtocolVersionDelta,
            AgentRegistry,
            SemanticOntology,
            Task,
            AgentMessage,
            MappingFailureLog,
        )
        await conn.run_sync(SQLModel.metadata.create_all)
