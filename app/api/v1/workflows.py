from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import get_current_principal, verify_engram_token
from app.db.session import get_session
from app.db.models import Workflow, WorkflowSchedule, Task
from app.messaging.multi_agent_orchestrator import MultiAgentOrchestrator
from app.services.workflow_runner import create_task_from_workflow

router = APIRouter()
logger = structlog.get_logger(__name__)


class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    command: str
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True


class WorkflowUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    command: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    command: str
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None


class WorkflowRunResponse(BaseModel):
    workflow_id: uuid.UUID
    task_id: uuid.UUID
    status: str


class WorkflowScheduleRequest(BaseModel):
    interval_minutes: Optional[int] = None
    interval_seconds: Optional[int] = None
    enabled: bool = True
    start_at: Optional[datetime] = None


class WorkflowScheduleResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    interval_seconds: int
    enabled: bool
    next_run_at: datetime
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class WorkflowTaskResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    last_error: Optional[str] = None


def _definition_from_request(command: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {"command": command, "metadata": metadata or {}}


def _workflow_to_response(workflow: Workflow) -> WorkflowResponse:
    definition = workflow.definition or {}
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        command=definition.get("command") or "",
        metadata=definition.get("metadata") or {},
        is_active=workflow.is_active,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        last_run_at=workflow.last_run_at,
    )


def _interval_seconds(req: WorkflowScheduleRequest) -> int:
    if req.interval_seconds is not None:
        return int(req.interval_seconds)
    if req.interval_minutes is not None:
        return int(req.interval_minutes) * 60
    return 0


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    request: WorkflowCreateRequest,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    orchestrator = MultiAgentOrchestrator()
    plan = orchestrator._generate_plan(request.command)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task parser could not determine a multi-agent plan. Please name the agents (e.g., Claude, Perplexity, Slack) in your workflow.",
        )

    eat_token = principal.get("_raw_token") if principal.get("type") == "EAT" else None

    workflow = Workflow(
        user_id=user_uuid,
        name=request.name,
        description=request.description,
        definition=_definition_from_request(request.command, request.metadata),
        eat=eat_token,
        is_active=request.is_active,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return _workflow_to_response(workflow)


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    limit: int = 50,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = (
        select(Workflow)
        .where(Workflow.user_id == user_uuid)
        .order_by(Workflow.updated_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    workflows = res.scalars().all()
    return [_workflow_to_response(wf) for wf in workflows]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user_uuid)
    res = await db.execute(stmt)
    workflow = res.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _workflow_to_response(workflow)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: uuid.UUID,
    request: WorkflowUpdateRequest,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user_uuid)
    res = await db.execute(stmt)
    workflow = res.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if request.command is not None:
        orchestrator = MultiAgentOrchestrator()
        plan = orchestrator._generate_plan(request.command)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Task parser could not determine a multi-agent plan. Please name the agents (e.g., Claude, Perplexity, Slack) in your workflow.",
            )
        current_definition = workflow.definition or {}
        workflow.definition = _definition_from_request(
            request.command,
            request.metadata if request.metadata is not None else current_definition.get("metadata"),
        )
    elif request.metadata is not None:
        definition = workflow.definition or {}
        definition["metadata"] = request.metadata
        workflow.definition = definition

    if request.name is not None:
        workflow.name = request.name
    if request.description is not None:
        workflow.description = request.description
    if request.is_active is not None:
        workflow.is_active = request.is_active

    workflow.updated_at = datetime.now(timezone.utc)
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return _workflow_to_response(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user_uuid)
    res = await db.execute(stmt)
    workflow = res.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    await db.delete(workflow)
    await db.commit()
    return None


@router.post("/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user_uuid)
    res = await db.execute(stmt)
    workflow = res.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    eat = principal.get("_raw_token") if principal.get("type") == "EAT" else None
    if eat:
        try:
            verify_engram_token(eat)
        except Exception as exc:
            raise HTTPException(status_code=403, detail=f"EAT Verification failed: {str(exc)}")

    task = await create_task_from_workflow(db, workflow, eat_override=eat or workflow.eat)
    return {"workflow_id": workflow.id, "task_id": task.id, "status": task.status}


@router.get("/{workflow_id}/tasks", response_model=List[WorkflowTaskResponse])
async def list_workflow_tasks(
    workflow_id: uuid.UUID,
    limit: int = 20,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = (
        select(Task)
        .where(Task.workflow_id == workflow_id, Task.user_id == user_uuid)
        .order_by(Task.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    tasks = res.scalars().all()
    return [
        WorkflowTaskResponse(
            id=task.id,
            status=str(task.status),
            created_at=task.created_at,
            updated_at=task.updated_at,
            last_error=task.last_error,
        )
        for task in tasks
    ]


@router.get("/{workflow_id}/schedule", response_model=WorkflowScheduleResponse)
async def get_workflow_schedule(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = select(WorkflowSchedule).where(
        WorkflowSchedule.workflow_id == workflow_id,
        WorkflowSchedule.user_id == user_uuid,
    )
    res = await db.execute(stmt)
    schedule = res.scalars().first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Workflow schedule not found")
    return schedule


@router.post("/{workflow_id}/schedule", response_model=WorkflowScheduleResponse)
async def upsert_workflow_schedule(
    workflow_id: uuid.UUID,
    request: WorkflowScheduleRequest,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    interval_seconds = _interval_seconds(request)
    if interval_seconds <= 0:
        raise HTTPException(status_code=422, detail="interval_seconds or interval_minutes must be provided.")

    wf_stmt = select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user_uuid)
    wf_res = await db.execute(wf_stmt)
    workflow = wf_res.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not workflow.eat:
        raise HTTPException(status_code=400, detail="Workflow does not have a stored EAT. Please run it once while authenticated.")

    stmt = select(WorkflowSchedule).where(
        WorkflowSchedule.workflow_id == workflow_id,
        WorkflowSchedule.user_id == user_uuid,
    )
    res = await db.execute(stmt)
    schedule = res.scalars().first()

    now = datetime.now(timezone.utc)
    start_at = request.start_at or now + timedelta(seconds=interval_seconds)
    if schedule:
        schedule.interval_seconds = interval_seconds
        schedule.enabled = request.enabled
        schedule.next_run_at = start_at
        schedule.updated_at = now
    else:
        schedule = WorkflowSchedule(
            workflow_id=workflow_id,
            user_id=user_uuid,
            interval_seconds=interval_seconds,
            enabled=request.enabled,
            next_run_at=start_at,
        )
        db.add(schedule)

    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.delete("/{workflow_id}/schedule", status_code=204)
async def delete_workflow_schedule(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_sub = principal.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Subject missing in token.")
    try:
        user_uuid = uuid.UUID(str(user_sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user identifier in token.")

    stmt = select(WorkflowSchedule).where(
        WorkflowSchedule.workflow_id == workflow_id,
        WorkflowSchedule.user_id == user_uuid,
    )
    res = await db.execute(stmt)
    schedule = res.scalars().first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Workflow schedule not found")

    await db.delete(schedule)
    await db.commit()
    return None
