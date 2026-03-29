import os
from urllib.parse import parse_qsl, urlsplit, urlunsplit
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from app.core.config import settings
from typing import AsyncGenerator

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

import asyncio
import logging

logger = logging.getLogger(__name__)

async def init_db():
    retries = 15
    delay = 4
    for i in range(retries):
        try:
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
                    User,
                    PermissionProfile,
                    ProviderCredential,
                    Workflow,
                    WorkflowSchedule,
                )
                await conn.run_sync(SQLModel.metadata.create_all)
                if engine.dialect.name == "postgresql":
                    # Advisory lock to prevent workers from clashing
                    await conn.execute(text("SELECT pg_advisory_xact_lock(42)"))
                    await _ensure_timestamptz(conn)
                    await _ensure_extra_columns(conn)
            logger.info("Database initialized successfully. Waiting 3s for background workers to start against stable schema...")
            await asyncio.sleep(3)
            return
        except Exception as e:
            if i < retries - 1:
                logger.warning(f"Database connection failed (attempt {i+1}/{retries}): {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Database connection failed after {retries} attempts. Exiting.")
                raise e


async def _ensure_timestamptz(conn) -> None:
    columns = {
        "protocol_mapping": ["created_at", "updated_at"],
        "protocol_version_delta": ["created_at", "updated_at"],
        "agent_registry": ["last_seen"],
        "semantic_ontology": ["created_at"],
        "tasks": ["leased_until", "created_at", "updated_at", "completed_at", "dead_lettered_at"],
        "agent_messages": ["leased_until", "created_at", "updated_at", "acked_at"],
        "mapping_failure_logs": ["created_at"],
        "users": ["created_at", "updated_at"],
        "permission_profiles": ["created_at", "updated_at"],
        "provider_credentials": ["created_at", "updated_at"],
        "workflows": ["created_at", "updated_at", "last_run_at"],
        "workflow_schedules": ["created_at", "updated_at", "next_run_at", "last_run_at"],
    }

    for table, cols in columns.items():
        for col in cols:
            result = await conn.execute(
                text(
                    """
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = :table
                      AND column_name = :column
                    """
                ),
                {"table": table, "column": col},
            )
            data_type = result.scalar()
            if data_type == "timestamp without time zone":
                await conn.execute(
                    text(
                        f"ALTER TABLE {table} "
                        f"ALTER COLUMN {col} TYPE TIMESTAMP WITH TIME ZONE "
                        f"USING timezone('UTC', {col})"
                    )
                )


async def _ensure_extra_columns(conn) -> None:
    # Schema evolution: add columns that might be missing from older DB versions
    updates = [
        ("tasks", "workflow_id", "UUID", True),
        ("tasks", "user_id", "UUID", True),
        ("tasks", "target_agent_id", "UUID", True),
        ("tasks", "eat", "TEXT", False),
        ("tasks", "completed_at", "TIMESTAMP WITH TIME ZONE", False),
        ("tasks", "dead_lettered_at", "TIMESTAMP WITH TIME ZONE", False),
        ("agent_messages", "acked_at", "TIMESTAMP WITH TIME ZONE", False),
        ("workflows", "eat", "TEXT", False),
        ("workflows", "is_active", "BOOLEAN", False),
        ("agent_registry", "is_active", "BOOLEAN", False),
        ("users", "is_active", "BOOLEAN", False),
        ("mapping_failure_logs", "applied", "BOOLEAN", False),
    ]
    
    for table, col, col_type, create_index in updates:
        try:
            # Explicitly check for column existence for clearer logging
            result = await conn.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name=:table AND column_name=:column"),
                {"table": table, "column": col}
            )
            if not result.scalar():
                logger.info(f"MIGRATION: Adding column {table}.{col} ({col_type})...")
                await conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                )
                if create_index:
                    index_name = f"ix_{table}_{col}"
                    await conn.execute(
                        text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({col})")
                    )
            else:
                logger.debug(f"Schema check: {table}.{col} already exists.")
        except Exception as e:
            logger.error(f"CRITICAL Schema Error on {table}.{col}: {e}")
