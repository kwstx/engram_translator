from typing import Any, Dict, Optional
import json
import structlog
from app.core.redis_client import get_redis_client
from app.core.config import settings

logger = structlog.get_logger(__name__)

class FederationSession:
    """
    Manages lightweight session state in Redis keyed by EAT tokens.
    Permits CLI-local workflows to delegate to MCP-remote agents (or A2A peers)
    without re-registration or semantic loss.
    """
    SESSION_PREFIX = "federation:session:"
    TTL = 3600  # 1 hour default

    def __init__(self, eat_jti: str):
        self.jti = eat_jti
        self.redis = get_redis_client()
        self.key = f"{self.SESSION_PREFIX}{self.jti}"

    async def update_state(self, category: str, data: Dict[str, Any]):
        """
        Updates session state for a specific category (e.g., 'artifacts', 'context', 'outputs').
        """
        if not self.redis:
            logger.warning("Redis not available, session state not persisted", jti=self.jti)
            return

        current_val = self.redis.get(self.key)
        state = json.loads(current_val) if current_val else {}
        
        state[category] = data
        
        self.redis.setex(self.key, self.TTL, json.dumps(state))
        logger.info("Federation session state updated", jti=self.jti, category=category)

    async def get_state(self) -> Dict[str, Any]:
        """Retrieves the full session state."""
        if not self.redis:
            return {}
        
        val = self.redis.get(self.key)
        return json.loads(val) if val else {}

    async def clear(self):
        """Removes the session state from Redis."""
        if self.redis:
            self.redis.delete(self.key)
