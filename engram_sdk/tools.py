from typing import Dict, Iterable, List

from .types import ToolDefinition


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> ToolDefinition:
        self._tools[tool.name] = tool
        return tool

    def register_many(self, tools: Iterable[ToolDefinition]) -> List[ToolDefinition]:
        registered = []
        for tool in tools:
            registered.append(self.register(tool))
        return registered

    def list(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def capabilities(self) -> List[str]:
        return sorted(self._tools.keys())
