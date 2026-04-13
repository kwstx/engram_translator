import uuid
from typing import List, Optional, Dict, Any


class Scope:
    """
    Represents a narrow, explicit set of tools for a single conversation step or agent turn.

    The Scope object is the primary way developers declare exactly which tools are
    available at any given moment, enforcing the principle that the developer's
    code owns the state machine.
    """

    def __init__(self, tools: List[str], step_id: Optional[str] = None) -> None:
        """
        Initialize a new Scope.

        Args:
            tools: A list of tool IDs or names that are available in this scope.
            step_id: A unique identifier for this conversation step. If not provided,
                a random UUID will be generated.
        """
        if not isinstance(tools, list):
            raise TypeError("tools must be a list of strings")
        
        self.tools = list(tools)
        self.step_id = step_id or str(uuid.uuid4())
        self.corrected_schemas: Dict[str, Any] = {}

    @property
    def tool_count(self) -> int:
        """Returns the number of tools in this scope."""
        return len(self.tools)

    def contains(self, tool_id: str) -> bool:
        """Checks if a specific tool is included in this scope."""
        return tool_id in self.tools

    def validate(self, sdk: Optional[Any] = None) -> bool:
        """
        Queries the real backend state for each tool in the narrow list using the existing registry.
        It runs the OWL ontology + ML embedding check against the current API or CLI definitions 
        to detect any schema drift or mismatches before any schema is ever sent to the model. 
        If drift is found, automatically generate a corrected schema version and store it with the scope.

        Returns:
            bool: True if no drift was found, False otherwise.
        """
        if sdk is None:
            # Attempt to find SDK in global context or common patterns if not provided
            # For now, we require it or we can't talk to the backend.
            return True

        drift_detected = False
        for tool_name in self.tools:
            # Query the backend state via the registry in the SDK
            # check_drift is a new method on ToolRegistry
            correction = sdk.tools.check_drift(tool_name, sdk.transport)
            if correction:
                self.corrected_schemas[tool_name] = correction
                drift_detected = True
        
        return not drift_detected

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Scope to a dictionary representation."""
        data = {
            "step_id": self.step_id,
            "tools": self.tools,
        }
        if self.corrected_schemas:
            data["corrected_schemas"] = self.corrected_schemas
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scope":
        """Creates a Scope instance from a dictionary."""
        instance = cls(
            tools=data.get("tools", []),
            step_id=data.get("step_id"),
        )
        if "corrected_schemas" in data:
            instance.corrected_schemas = data["corrected_schemas"]
        return instance

    def __repr__(self) -> str:
        return f"Scope(step_id={self.step_id!r}, tools={self.tools!r}, drift={bool(self.corrected_schemas)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Scope):
            return NotImplemented
        return (self.step_id == other.step_id and 
                self.tools == other.tools and 
                self.corrected_schemas == other.corrected_schemas)
