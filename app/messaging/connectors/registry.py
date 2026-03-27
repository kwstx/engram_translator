import structlog
from typing import Dict, Any, Type, Optional, List
from .base import BaseConnector
from .claude import ClaudeConnector
from .perplexity import PerplexityConnector
from .slack import SlackConnector
from .openclaw import OpenClawConnector
from .mirofish import MiroFishConnector

logger = structlog.get_logger(__name__)

class ConnectorRegistry:
    """
    Registry for organizing and retrieving tool access connectors.
    This architecture allows adding new tools without modifying the 
    core orchestration layer.
    """

    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector):
        """Registers a connector instance."""
        name = connector.name.upper()
        self._connectors[name] = connector
        logger.info("Connector registered", name=name)

    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """Retrieves a connector by name."""
        return self._connectors.get(name.upper())

    def list_connectors(self) -> List[str]:
        """Lists all registered connectors."""
        return list(self._connectors.keys())

    def has_connector(self, name: str) -> bool:
        """Checks if a connector exists."""
        return name.upper() in self._connectors

def get_default_registry() -> ConnectorRegistry:
    """
    Returns a ConnectorRegistry prepopulated with the standard toolset.
    """
    registry = ConnectorRegistry()
    registry.register(ClaudeConnector())
    registry.register(PerplexityConnector())
    registry.register(SlackConnector())
    registry.register(OpenClawConnector())
    registry.register(MiroFishConnector())
    return registry
