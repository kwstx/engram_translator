from .client import EngramSDK
from .scope import Scope, ScopeCache
from .types import ToolDefinition, TaskLease, TaskSubmissionResult, TaskExecution, TaskResponse, TranslationResponse, MappingSuggestion, ToolCall
from .execution import TaskExecutor
from .adapter import RuntimeAdapter, ScopeValidationError
from .control_plane import ControlPlane
from .routing import RoutingEngine
from .exceptions import (
    EngramSDKError,
    EngramAuthError,
    EngramRequestError,
    EngramResponseError,
)
from .global_data import GlobalData, get_global_data, delete_data, DELETE_DATA_TOOL
from .controlled_tools import (
    PROCESS_IDENTITY_TOOL,
    VERIFY_CLEARANCE_TOOL,
    GENERATE_REPORT_TOOL,
    SCRUB_DATA_TOOL,
    process_raw_identification,
    verify_security_clearance,
    generate_access_report,
    scrub_sensitive_data
)

from typing import List, Optional

def scope(name: str, tools: Optional[List[str]] = None, sdk: Optional[EngramSDK] = None) -> Scope:
    """
    Convenience method to create and activate a tool scope.
    If no SDK instance is provided, a default EngramSDK() will be used.
    """
    if sdk is None:
        sdk = EngramSDK()
    return sdk.scope(name, tools=tools)

def flow(name: str, sdk: Optional[EngramSDK] = None) -> ControlPlane:
    """
    Convenience method to enter a specific governed flow.
    """
    if sdk is None:
        sdk = EngramSDK()
    return ControlPlane(sdk).flow(name)

# Lazy-loaded default control plane for 'with engram.control_plane.step(...)'
_cp_instance = None

def _get_cp():
    global _cp_instance
    if _cp_instance is None:
        _cp_instance = ControlPlane(EngramSDK())
    return _cp_instance

import sys

class _EngramModule(sys.modules[__name__].__class__):
    @property
    def control_plane(self):
        return _get_cp()

sys.modules[__name__].__class__ = _EngramModule

__all__ = [
    "EngramSDK",
    "Scope",
    "scope",
    "flow",
    "control_plane",
    "ControlPlane",

    "ScopeCache",
    "ToolDefinition",
    "TaskLease",
    "TaskSubmissionResult",
    "TaskExecution",
    "TaskResponse",
    "TaskExecutor",
    "TranslationResponse",
    "MappingSuggestion",
    "ToolCall",
    "EngramSDKError",
    "ScopeValidationError",
    "RuntimeAdapter",
    "EngramAuthError",
    "EngramRequestError",
    "EngramResponseError",
    "GlobalData",
    "get_global_data",
    "PROCESS_IDENTITY_TOOL",
    "VERIFY_CLEARANCE_TOOL",
    "GENERATE_REPORT_TOOL",
    "DELETE_DATA_TOOL",
    "SCRUB_DATA_TOOL",
    "process_raw_identification",
    "verify_security_clearance",
    "generate_access_report",
    "delete_data",
    "scrub_sensitive_data",
    "RoutingEngine"
]

