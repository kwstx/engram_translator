from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import json

from .exceptions import EngramSDKError

if TYPE_CHECKING:
    from .client import EngramSDK
    from .scope import Scope

class ScopeValidationError(EngramSDKError):
    """Raised when a tool call is attempted outside the active validated scope."""
    pass

class RuntimeAdapter:
    """
    The RuntimeAdapter acts as a security and validation gate for agent tool calls.
    
    It enforces the 'developer-in-the-loop' principle by ensuring that at inference time,
    only tools and schemas that were explicitly validated and included in the active 
    scope can be executed. 
    
    If the model attempts to hallucinate a tool or use an outdated schema, the adapter
    rejects the call immediately before it reaches the backend.
    """

    def __init__(self, sdk: EngramSDK, scope: Scope):
        self._sdk = sdk
        self._scope = scope

    def call(self, tool_name: str, arguments: Dict[str, Any], _is_retry: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Validates and executes a tool call within the current scope.
        
        Args:
            tool_name: The name or ID of the tool to call.
            arguments: The arguments for the tool call.
            _is_retry: Internal flag to prevent infinite loops during self-healing.
            **kwargs: Additional parameters passed to the backend (e.g. action name).
            
        Returns:
            The result of the tool execution.
            
        Raises:
            ScopeValidationError: If the tool is not in the active scope.
        """
        # 1. Enforce Scope Membership: The model proposes, the code disposes.
        if not self._scope.contains(tool_name):
            allowed = ", ".join(self._scope.tools)
            raise ScopeValidationError(
                f"Blocked unauthorized tool call: '{tool_name}' is not in the active scope. "
                f"Current validated tools for this turn are: [{allowed}]. "
                "Enforcement triggered at inference time."
            )

        # 2. Schema Adaptation
        # If we have a corrected schema for this tool (from drift detection), 
        # we log that we are using it. The backend already knows about this 
        # from the activate() call.
        corrected = self._scope.corrected_schemas.get(tool_name)

        # 3. Resolve Tool ID for Backend (mcp.call_tool expects UUID)
        tool_id = self._scope.tool_ids.get(tool_name, tool_name)

        # 4. Forward Call via MCP Protocol
        payload = {
            "method": "mcp.call_tool",
            "params": {
                "tool_id": tool_id,
                "arguments": arguments,
                "scope_id": self._scope.step_id,
                "corrected_schema": corrected,
                **kwargs
            },
            "id": 1,
            "jsonrpc": "2.0"
        }

        try:
            response = self._sdk.transport.request_json(
                "POST", 
                "/registry/mcp/call", 
                json_body=payload
            )
            
            if "error" in response:
                error = response["error"]
                # 5. SELF-HEALING FALLBACK: If we encounter drift that validation missed
                # We check for schema deviations (JSON-RPC Invalid Params -32602 or specific drift hints)
                if not _is_retry and self._is_unexpected_drift(error):
                    return self._apply_self_healing(tool_name, arguments, error, **kwargs)
                return response
            
            return response.get("result", {})
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Transport error: {str(e)}"},
                "id": 1
            }

    def _is_unexpected_drift(self, error: Dict[str, Any]) -> bool:
        """Determines if the error response indicates a schema drift/mismatch."""
        code = error.get("code")
        msg = error.get("message", "").lower()
        
        # -32602 is 'Invalid params' in JSON-RPC
        is_param_error = (code == -32602)
        
        # Check for keywords indicating structural changes
        drift_keywords = ["schema", "drift", "mismatch", "unexpected", "missing", "property"]
        has_keywords = any(k in msg for k in drift_keywords)
        
        return is_param_error or has_keywords

    def _apply_self_healing(self, tool_name: str, arguments: Dict[str, Any], error: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Attempts a quick runtime fix for unexpected drift by re-evaluating the tool schema.
        """
        print("\n" + "!" * 80)
        print(f"!!! [SELF-HEALING] UNEXPECTED DRIFT DETECTED FOR: '{tool_name}'")
        print(f"!!! Error: {error.get('message')}")
        print("!!! Attempting last-resort runtime schema refresh...")
        print("!" * 80 + "\n")

        # 1. Mark the event for developers
        self._mark_drift_event(tool_name, arguments, error)

        # 2. Try to refresh drift status immediately
        try:
            # Re-run drift check for just this tool
            correction = self._sdk.tools.check_drift(tool_name, self._sdk.transport)
            if correction:
                print(f"[SELF-HEALING] Success! Found updated schema for '{tool_name}'. Retrying...")
                self._scope.corrected_schemas[tool_name] = correction
                # Retry once with the updated knowledge
                return self.call(tool_name, arguments, _is_retry=True, **kwargs)
            else:
                print(f"[SELF-HEALING] No new schema correction found for '{tool_name}'. Fix failed.")
        except Exception as e:
            print(f"[SELF-HEALING] Fix process failed: {str(e)}")

        # If fix failed, return original error
        return {"jsonrpc": "2.0", "error": error, "id": 1}

    def _mark_drift_event(self, tool_name: str, arguments: Dict[str, Any], error: Dict[str, Any]):
        """Persists the drift event to a dedicated log for developer review."""
        import os
        import json
        import time
        from pathlib import Path

        log_dir = Path.home() / ".engram"
        log_file = log_dir / "drift_events.jsonl"
        
        # Redact potentially sensitive arguments for logging (keep keys, hide values)
        redacted_args = {k: "..." for k in arguments.keys()}
        
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "scope_id": self._scope.step_id,
            "tool_name": tool_name,
            "error_message": error.get("message"),
            "drift_context": redacted_args,
            "status": "SELF_HEALING_TRIGGERED",
            "resolution": "SCHEMA_REFRESH"
        }

        try:
            os.makedirs(log_dir, exist_ok=True)
            with open(log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass

    def __repr__(self) -> str:
        return f"RuntimeAdapter(scope={self._scope.name or self._scope.step_id}, tools={len(self._scope.tools)})"

