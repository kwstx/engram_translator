import asyncio
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.db.session import engine
from app.db.models import ProtocolVersionDelta, ProtocolType


DEFAULT_A2A_V1_TO_V2: Dict[str, Any] = {
    "rename": {
        "old_field": "new_field",
    }
}


async def seed_version_deltas() -> None:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        await _upsert_delta(
            session=session,
            protocol=ProtocolType.A2A,
            from_version="1",
            to_version="2",
            delta_rules=DEFAULT_A2A_V1_TO_V2,
        )
        await session.commit()


async def _upsert_delta(
    session: AsyncSession,
    protocol: ProtocolType,
    from_version: str,
    to_version: str,
    delta_rules: Dict[str, Any],
) -> None:
    stmt = select(ProtocolVersionDelta).where(
        ProtocolVersionDelta.protocol == protocol,
        ProtocolVersionDelta.from_version == from_version,
        ProtocolVersionDelta.to_version == to_version,
    )
    result = await session.execute(stmt)
    existing = result.scalars().first()

    if existing:
        existing.delta_rules = delta_rules
        session.add(existing)
        return

    session.add(
        ProtocolVersionDelta(
            protocol=protocol,
            from_version=from_version,
            to_version=to_version,
            delta_rules=delta_rules,
        )
    )


if __name__ == "__main__":
    asyncio.run(seed_version_deltas())
