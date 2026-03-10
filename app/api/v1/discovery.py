from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import AgentRegistry, ProtocolMapping
from pydantic import BaseModel, Field
from typing import List
from app.services.discovery import DiscoveryService

router = APIRouter(prefix="/discovery", tags=["Discovery"])

class AgentDiscoveryRequest(BaseModel):
    protocols: List[str] = Field(..., description="List of protocols supported by the agent")
    semantic_tags: List[str] = Field(..., description="Semantic capabilities or tags to match")

@router.post("/", response_model=List[AgentRegistry])
async def discover_agents(
    request: AgentDiscoveryRequest, 
    db: Session = Depends(get_session)
):
    """
    Discovers agents that either support the requested protocols directly 
    or can be reached via protocol translation.
    """
    # 1. Determine compatible protocols (direct + translatable)
    requested_protocols = request.protocols
    
    # Query for protocol mappings starting from source protocols
    mapping_stmt = select(ProtocolMapping).where(ProtocolMapping.source_protocol.in_(requested_protocols))
    mapping_results = await db.execute(mapping_stmt)
    mappings = mapping_results.scalars().all()
    
    # Target protocols we can translate into
    translatable_to = {m.target_protocol for m in mappings}
    eligible_protocols = set(requested_protocols) | translatable_to
    
    # 2. Search AgentRegistry for matching agents
    # Match any agent supporting at least one eligible protocol
    stmt = select(AgentRegistry).where(
        AgentRegistry.supported_protocols.overlap(list(eligible_protocols))
    )
    
    # 3. Apply semantic tag filtering
    if request.semantic_tags:
        # Match agents having at least one overlapping semantic tag
        stmt = stmt.where(
            AgentRegistry.semantic_tags.overlap(request.semantic_tags)
        )
        
    results = await db.execute(stmt)
    agents = results.scalars().all()
    
    return agents

@router.get("/collaborators", response_model=List[AgentRegistry])
async def get_collaborators(
    protocols: str,
    min_score: float = 0.7,
    db: Session = Depends(get_session)
):
    """
    Finds collaborative agents based on compatibility score formula:
    (shared_protocols + mappable_protocols) / total_protocols >= min_score
    Protocols should be a comma-separated list of strings.
    """
    protocol_list = [p.strip() for p in protocols.split(",") if p.strip()]
    collaborators = await DiscoveryService.find_collaborators(
        session=db,
        source_protocols=protocol_list,
        min_score=min_score
    )
    return collaborators
