from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime, timezone
import structlog
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EntityState

logger = structlog.get_logger(__name__)


class ConflictResolver:
    """
    Resolves conflicts between incoming ontology payloads using simple ontological policies.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve(
        self,
        *,
        entity_key: str,
        incoming_payload: Dict[str, Any],
        policy: str = "last_write_wins",
        source_id: Optional[str] = None,
        source_timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        result = await self.session.execute(
            select(EntityState).where(EntityState.entity_key == entity_key)
        )
        current = result.scalars().first()

        effective_policy = policy or (current.conflict_policy if current else "last_write_wins")
        incoming_ts = source_timestamp or datetime.now(timezone.utc)

        if not current:
            state = EntityState(
                entity_key=entity_key,
                ontology_payload=incoming_payload,
                conflict_policy=effective_policy,
                source_id=source_id,
                updated_at=incoming_ts,
            )
            self.session.add(state)
            await self.session.commit()
            return incoming_payload

        resolved_payload = current.ontology_payload or {}
        if effective_policy == "merge":
            resolved_payload = self._deep_merge(resolved_payload, incoming_payload)
        else:
            # Default: last-write-wins
            if incoming_ts >= current.updated_at:
                resolved_payload = incoming_payload

        current.ontology_payload = resolved_payload
        current.updated_at = incoming_ts
        current.source_id = source_id or current.source_id
        current.conflict_policy = effective_policy
        current.version += 1
        self.session.add(current)
        await self.session.commit()

        logger.info(
            "Resolved entity conflict",
            entity_key=entity_key,
            policy=effective_policy,
            version=current.version,
        )
        return resolved_payload

    def _deep_merge(self, base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(base)
        for key, value in incoming.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
