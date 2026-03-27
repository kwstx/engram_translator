from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Dict, Any, Optional
import uuid
import structlog
from datetime import datetime, timezone
from pydantic import BaseModel

from app.db.session import get_session
from app.core.security import get_current_principal, verify_engram_token
from app.db.models import Task, TaskStatus
from app.messaging.multi_agent_orchestrator import MultiAgentOrchestrator

router = APIRouter()
logger = structlog.get_logger(__name__)

class TaskSubmitRequest(BaseModel):
    command: str
    metadata: Optional[Dict[str, Any]] = None

class TaskSubmitResponse(BaseModel):
    task_id: uuid.UUID
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    results: Optional[Dict[str, Any]] = None
    last_error: Optional[str] = None
    message: Optional[str] = None

@router.post("/submit", response_model=TaskSubmitResponse)
async def submit_multi_agent_task(
    request: TaskSubmitRequest,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    """
    Submits a complex natural language task for multi-agent execution.
    Verifies the EAT, parses the task into a plan, and enqueues it.
    """
    eat = principal.get("_raw_token")
    if not eat:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Engram Access Token (EAT)."
        )

    # 1. Verify EAT quickly for initial validation
    try:
        verify_engram_token(eat)
    except Exception as e:
        logger.error("Initial EAT validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"EAT Verification failed: {str(e)}"
        )

    # 2. Parse the task into a plan to ensure it's valid
    orchestrator = MultiAgentOrchestrator()
    plan = orchestrator._generate_plan(request.command)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task parser could not determine a multi-agent plan. Please name the agents (e.g., Claude, Perplexity, Slack) in your request."
        )

    # 3. Create the Task record
    task = Task(
        source_protocol="NL",
        target_protocol="MULTI_AGENT",
        source_message={
            "command": request.command,
            "plan": plan,
            "metadata": request.metadata or {}
        },
        eat=eat,
        status=TaskStatus.PENDING
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    logger.info("Task submitted", task_id=task.id, user_id=principal.get("sub"))
    
    return {
        "task_id": task.id,
        "status": task.status,
        "message": f"Task accepted and split into {len(plan)} agent steps."
    }

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    """
    Retrieves the status and results of a submitted task.
    """
    stmt = select(Task).where(Task.id == task_id)
    res = await db.execute(stmt)
    task = res.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Basic authorization: Verify user is the same as the one who submitted?
    # For now, we allow reading tasks if they exist, but ideally we check principal['sub']
    
    return task

@router.get("/", response_model=List[TaskStatusResponse])
async def list_tasks(
    limit: int = 10,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    """
    Lists recent tasks for the authenticated user.
    """
    # Filtering by user_id would require extraction from EAT
    stmt = select(Task).order_by(Task.created_at.desc()).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()
