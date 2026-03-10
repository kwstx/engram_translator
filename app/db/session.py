from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from app.core.config import settings
from typing import AsyncGenerator

# Use SQLModel engines for compatibility
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

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
