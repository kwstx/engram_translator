from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ToolAction:
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = None
    required_permissions: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    actions: List[ToolAction] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = None
    required_permissions: List[str] = field(default_factory=list)
    version: Optional[str] = None
    tags: List[str] = field(default_factory=list)



@dataclass(frozen=True)
class TaskLease:
    message_id: str
    task_id: str
    payload: Dict[str, Any]
    leased_until: datetime


@dataclass(frozen=True)
class TaskSubmissionResult:
    task_id: str
    status: str
    message: Optional[str] = None


@dataclass(frozen=True)
class MappingSuggestion:
    source_field: str
    suggestion: Optional[str] = None
    confidence: Optional[float] = None
    applied: bool = False


@dataclass(frozen=True)
class TranslationResponse:
    status: str
    message: str
    payload: Dict[str, Any]
    mapping_suggestions: List[MappingSuggestion] = field(default_factory=list)


@dataclass(frozen=True)
class TaskExecution:
    message_id: str
    task_id: str
    payload: Dict[str, Any]
    leased_until: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskResponse:
    status: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    protocol: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
