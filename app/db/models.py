from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class ProtocolMapping(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source_protocol: str # e.g., "A2A"
    target_protocol: str # e.g., "MCP"
    mapping_rules: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SemanticOntology(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str # e.g., "e-commerce-ontology"
    namespace: str # e.g., "http://schema.org/"
    rdf_content: Optional[str] = Field(default=None) # Serialized RDF/XML or Turtle
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentRegistry(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agent_id: str
    supported_protocols: List[str] = Field(default=[], sa_column=Column(JSONB))
    capabilities: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    endpoint: str
    status: str = "active"
    last_seen: datetime = Field(default_factory=datetime.utcnow)
