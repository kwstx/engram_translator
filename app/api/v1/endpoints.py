from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import AgentRegistry, ProtocolMapping, SemanticOntology
from app.messaging.events import rabbitmq
from app.semantic.ontology_manager import ontology_manager
from typing import List, Dict, Any
import uuid

router = APIRouter()

@router.post("/register", response_model=AgentRegistry, tags=["Registry"])
async def register_agent(agent: AgentRegistry, db: Session = Depends(get_session)):
    """Registers a new agent with its supported protocols and capabilities."""
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # Notify other services via RabbitMQ
    await rabbitmq.publish("agent.registered", {"agent_id": str(agent.id)})
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
async def translate_message(source_agent: str, target_agent: str, payload: Dict[str, Any], db: Session = Depends(get_session)):
    """Translates a message from source agent protocol to target agent protocol."""
    # 1. Look up source and target agents
    # 2. Identify protocol mapping rules
    # 3. Apply semantic mapping using ontology_manager
    # 4. Return translated payload or queue it for handoff
    # Placeholder for translation logic
    return {
        "status": "pending",
        "message": f"Translating message from {source_agent} to {target_agent}",
        "payload": payload
    }

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
