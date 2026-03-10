from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import (
    AgentRegistry,
    SemanticOntology,
    Task,
    TaskStatus,
    AgentMessage,
    AgentMessageStatus,
)
from app.semantic.ontology_manager import ontology_manager
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.core.security import require_scopes
from app.core.metrics import record_translation_error, record_translation_success
from app.core.config import settings
from app.services.queue import lease_agent_message

router = APIRouter(dependencies=[require_scopes([])])

@router.post("/register", response_model=AgentRegistry, tags=["Registry"])
async def register_agent(agent: AgentRegistry, db: Session = Depends(get_session)):
    """Registers a new agent with its supported protocols and capabilities."""
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.get("/discover", response_model=List[AgentRegistry], tags=["Registry"])
async def discover_agents(protocol: str = None, capability: str = None, db: Session = Depends(get_session)):
    """Discovers agents capable of handling specific protocols or tasks."""
    statement = select(AgentRegistry)
    if protocol:
        statement = statement.where(AgentRegistry.supported_protocols.contains([protocol]))
    # Capability filtering can be added here with more logic
    results = await db.execute(statement)
    return results.scalars().all()

@router.post("/translate", tags=["Translation"])
async def translate_message(
    source_agent: str,
    target_agent: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_session),
    _principal: Dict[str, Any] = require_scopes(["translate:a2a"]),
):
    """Translates a message from source agent protocol to target agent protocol."""
    # 1. Look up source and target agents
    # 2. Identify protocol mapping rules
    # 3. Apply semantic mapping using ontology_manager
    # 4. Return translated payload or queue it for handoff
    # Placeholder for translation logic
    try:
        response = {
            "status": "pending",
            "message": f"Translating message from {source_agent} to {target_agent}",
            "payload": payload,
        }
        record_translation_success("api")
        return response
    except Exception:
        record_translation_error("api")
        raise


class TaskEnqueueRequest(BaseModel):
    source_message: Dict[str, Any]
    source_protocol: str
    target_protocol: str
    target_agent_id: UUID
    max_attempts: int = Field(default_factory=lambda: settings.TASK_MAX_ATTEMPTS)


class TaskEnqueueResponse(BaseModel):
    task_id: UUID
    status: TaskStatus


class AgentMessageLeaseResponse(BaseModel):
    message_id: UUID
    task_id: UUID
    payload: Dict[str, Any]
    leased_until: datetime


@router.post("/queue/enqueue", response_model=TaskEnqueueResponse, tags=["Queue"])
async def enqueue_task(
    request: TaskEnqueueRequest,
    db: Session = Depends(get_session),
):
    task = Task(
        source_message=request.source_message,
        source_protocol=request.source_protocol,
        target_protocol=request.target_protocol,
        target_agent_id=request.target_agent_id,
        status=TaskStatus.PENDING,
        max_attempts=request.max_attempts,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskEnqueueResponse(task_id=task.id, status=task.status)


@router.post(
    "/agents/{agent_id}/messages/poll",
    response_model=AgentMessageLeaseResponse,
    tags=["Queue"],
)
async def poll_agent_messages(
    agent_id: UUID,
    lease_seconds: int = settings.AGENT_MESSAGE_LEASE_SECONDS,
    db: Session = Depends(get_session),
):
    message = await lease_agent_message(
        db,
        agent_id=agent_id,
        lease_owner=f"agent-{agent_id}",
        lease_seconds=lease_seconds,
    )
    if not message:
        return Response(status_code=204)
    return AgentMessageLeaseResponse(
        message_id=message.id,
        task_id=message.task_id,
        payload=message.payload,
        leased_until=message.leased_until,
    )


@router.post(
    "/agents/messages/{message_id}/ack",
    tags=["Queue"],
)
async def ack_agent_message(
    message_id: UUID,
    db: Session = Depends(get_session),
):
    result = await db.execute(
        select(AgentMessage).where(AgentMessage.id == message_id)
    )
    message = result.scalars().first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    if message.status == AgentMessageStatus.ACKED:
        return {"status": "acked", "message_id": str(message.id)}

    message.status = AgentMessageStatus.ACKED
    message.acked_at = datetime.now(timezone.utc)
    message.lease_owner = None
    message.leased_until = None
    message.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "acked", "message_id": str(message.id)}

@router.post("/ontology/upload", tags=["Ontology"])
async def upload_ontology(name: str, rdf_xml: str, db: Session = Depends(get_session)):
    """Uploads an RDF ontology for semantic mapping."""
    ontology = SemanticOntology(name=name, namespace="http://local.ontology/", rdf_content=rdf_xml)
    db.add(ontology)
    await db.commit()
    await db.refresh(ontology)
    
    # Load into memory-based RDFlib graph
    ontology_manager.load_ontology(rdf_xml, format="xml")
    return {"status": "success", "id": str(ontology.id)}
