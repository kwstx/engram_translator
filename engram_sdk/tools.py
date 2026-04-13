from typing import Dict, Iterable, List, Optional, Any

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

    def check_drift(self, tool_name: str, transport: Any) -> Optional[Dict[str, Any]]:
        """
        Queries the backend to detect if the tool's schema has drifted from 
        the real API/CLI definitions using OWL ontology + ML embedding.
        """
        try:
            from dataclasses import asdict
            
            local_tool = self._tools.get(tool_name)
            body = {}
            if local_tool:
                body["current_schema"] = asdict(local_tool)
            
            # The backend endpoint runs the OWL + ML comparison
            response = transport.request_json(
                "POST",
                f"/registry/tools/{tool_name}/validate",
                json_body=body,
            )
            
            if response.get("drift"):
                return response.get("corrected_schema")
        except Exception:
            # Silently return None if check fails, assuming no drift can be confirmed
            return None
        
        return None
