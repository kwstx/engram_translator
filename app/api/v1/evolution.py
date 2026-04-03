import uuid
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.db.session import get_session
from app.db.models import ToolFeedback, EvolutionFeedbackType, ToolEvolution
from app.core.security import get_current_principal
from app.services.evolution import ToolEvolutionService

router = APIRouter()
logger = structlog.get_logger(__name__)

class FeedbackSubmit(BaseModel):
    tool_id: uuid.UUID
    score: float = Field(..., ge=-1.0, le=1.0, description="Rating from -1 to 1 or 0 to 1")
    comment: Optional[str] = None
    feedback_type: EvolutionFeedbackType = EvolutionFeedbackType.RATING
    metadata: Dict[str, Any] = {}

class EvolutionResponse(BaseModel):
    id: uuid.UUID
    tool_id: uuid.UUID
    previous_version: str
    new_version: str
    change_type: str
    confidence_score: float

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_tool_feedback(
    request: FeedbackSubmit,
    db: Any = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    """
    Submits feedback (ratings, corrections) to the Evolution Engine via EAT token.
    Used for guidance of the Self-Evolving Tools logic.
    """
    user_id = uuid.UUID(principal["sub"]) if "sub" in principal else None
    eat = principal.get("_raw_token")
    
    feedback = ToolFeedback(
        tool_id=request.tool_id,
        user_id=user_id,
        eat_token=eat,
        score=request.score,
        comment=request.comment,
        feedback_type=request.feedback_type,
        metadata_json=request.metadata
    )
    
    db.add(feedback)
    await db.commit()
    logger.info("Tool feedback registered", tool_id=request.tool_id, score=request.score)
    return {"status": "success", "message": "Feedback recorded for tool evolution audit."}

@router.get("/history/{tool_id}", response_model=List[EvolutionResponse])
async def get_tool_evolution_history(
    tool_id: uuid.UUID,
    db: Any = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    """
    Returns the versioned history of improvements for a specific tool.
    """
    from sqlmodel import select
    stmt = select(ToolEvolution).where(ToolEvolution.tool_id == tool_id).order_by(ToolEvolution.applied_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_evolution_loop(
    db: Any = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    """
    Manually triggers the Celery-monitored evolution loop.
    (Self-Evolving Tools are usually evolved via background pipeline).
    """
    # Permission check (e.g., admin or system)
    # Mocking check for now
    
    service = ToolEvolutionService(db)
    # In a real environment, this would call .delay() on a Celery task.
    # Here we run synchronously if requested (or we could use a background task in FastAPI).
    await service.run_evolution_loop()
    
    return {"status": "accepted", "message": "Evolution pipeline trigger successful."}
