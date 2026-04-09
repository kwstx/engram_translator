import sqlite3
import os
import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
from app.semantic.mapper import SemanticMapper
from app.core.config import settings
import sys

try:
    from pyswip import Prolog
except (ImportError, OSError):
    class Prolog:
        def consult(self, *args, **kwargs): pass
        def query(self, *args, **kwargs): return []
        def assertz(self, *args, **kwargs): pass
        def retract(self, *args, **kwargs): pass

try:
    from pyDatalog import pyDatalog
    pyDatalog.create_terms('A, X, Y, Z, A2, Y2, Z2, latest_fact, fact_data')
except Exception:
    A = X = Y = Z = A2 = Y2 = Z2 = latest_fact = fact_data = None

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Memory"])

# ~/.engram/swarm_memory.db (Persistence for facts)
DB_PATH = os.path.expanduser("~/.engram/swarm_memory.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class MemoryWriteRequest(BaseModel):
    agent_id: str
    protocol: str
    payload: Dict[str, Any]

class MemoryQueryResponse(BaseModel):
    key: str
    value: Any
    agent_id: str
    timestamp: float

class SwarmMemory:
    def __init__(self):
        self.prolog = Prolog()
        
        # Setup SQLite for persistence
        self._init_db()
        
        # Load existing ontology
        ontology_folder = os.path.join(os.getcwd(), "app/semantic")
        ontology_file = os.path.join(ontology_folder, "protocols.owl")
        self.mapper = SemanticMapper(ontology_file)
        
        # Load existing facts from SQLite into Prolog
        self.load_memory()
        
        try:
            # Define conflict resolution rules in pyDatalog
            # latest_fact(Key, Value, Agent, Timestamp)
            (latest_fact(X, Y, A, Z) <= 
                fact_data(A, X, Y, Z) & 
                ~ (fact_data(A2, X, Y2, Z2) & (Z2 > Z)))
        except Exception:
            logger.warning("pyDatalog resolution rules not loaded")

    def _init_db(self):
        """Initializes the SQLite database for fact persistence."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    predicate TEXT,
                    value TEXT,
                    timestamp REAL,
                    protocol TEXT
                )
            """)
            conn.commit()

    def load_memory(self):
        """Loads facts from SQLite into the Prolog engine."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute("SELECT agent_id, predicate, value, timestamp FROM facts")
                count = 0
                for row in cursor:
                    agent, pred, val_str, ts = row
                    # Escape for Prolog
                    agent_safe = agent.replace("'", "\\'")
                    pred_safe = pred.replace("'", "\\'")
                    
                    # Try to parse JSON value if it was complex, else use as raw
                    try:
                        val = json.loads(val_str)
                    except:
                        val = val_str
                    
                    if isinstance(val, str):
                        escaped = val.replace("'", "\\'")
                        val_safe = f"'{escaped}'"
                    else:
                        val_safe = val
                    
                    self.prolog.assertz(f"fact('{agent_safe}', '{pred_safe}', {val_safe}, {ts})")
                    count += 1
                logger.info("Memory loaded from SQLite", path=DB_PATH, fact_count=count)
        except Exception as e:
            logger.error("Failed to load memory from SQLite", error=str(e))

    def write(self, agent_id: str, protocol: str, payload: Dict[str, Any]):
        """Reconciles payload fields using semantic mapper and stores them in SQLite + Prolog."""
        timestamp = datetime.now(timezone.utc).timestamp()
        flattened = self.mapper._flatten_dict(payload)
        facts_added = 0
        
        with sqlite3.connect(DB_PATH) as conn:
            for key, value in flattened.items():
                leaf_key = key.split('.')[-1]
                resolved = self.mapper.resolve_equivalent(leaf_key, protocol)
                concept = resolved.split(':')[-1] if ':' in resolved else leaf_key
                
                # 1. Save to SQLite
                val_str = json.dumps(value) if not isinstance(value, (str, int, float)) else str(value)
                conn.execute(
                    "INSERT INTO facts (agent_id, predicate, value, timestamp, protocol) VALUES (?, ?, ?, ?, ?)",
                    (agent_id, concept, val_str, timestamp, protocol)
                )
                
                # 2. Assert to Prolog for live reasoning
                agent_safe = agent_id.replace("'", "\\'")
                concept_safe = concept.replace("'", "\\'")
                
                if isinstance(value, str):
                    clean_val = value.replace("'", "\\'")
                    val_safe = f"'{clean_val}'"
                else:
                    val_safe = value
                
                self.prolog.assertz(f"fact('{agent_safe}', '{concept_safe}', {val_safe}, {timestamp})")
                facts_added += 1
            conn.commit()
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "facts_written": facts_added,
            "timestamp": timestamp
        }

    def check_exists(self, key: str, value: Any, agent_id: Optional[str] = None) -> bool:
        """Checks if a specific fact exists in memory (queries Prolog)."""
        val_safe = f"'{value}'" if isinstance(value, str) else value
        query_str = f"fact(A, '{key}', {val_safe}, T)"
        if agent_id:
            query_str = f"fact('{agent_id}', '{key}', {val_safe}, T)"
        
        results = list(self.prolog.query(query_str))
        return len(results) > 0

    def query(self, key: str, agent_id: Optional[str] = None):
        """Queries memory and resolves conflicts using pyDatalog latest-timestamp rules."""
        query_str = f"fact(A, '{key}', V, T)"
        if agent_id:
            query_str = f"fact('{agent_id}', '{key}', V, T)"
        
        prolog_results = list(self.prolog.query(query_str))
        if not prolog_results:
            return None
        
        pyDatalog.clear()
        for res in prolog_results:
            + fact_data(str(res['A']), key, res['V'], res['T'])
        
        res_list = latest_fact(key, Y, A, Z)
        if res_list:
            resolved = res_list[0]
            return {
                "key": resolved[0],
                "value": resolved[1],
                "agent_id": resolved[2],
                "timestamp": resolved[3]
            }
        return None

_memory_backend = None

def get_memory_backend() -> SwarmMemory:
    global _memory_backend
    if _memory_backend is None:
        _memory_backend = SwarmMemory()
    return _memory_backend

# We provide a wrapper for backward compatibility or direct use if needed
class SwarmMemoryProxy:
    def __getattr__(self, name):
        return getattr(get_memory_backend(), name)
        
memory_backend = SwarmMemoryProxy()

@router.post("/memory/write")
async def write_memory(request: MemoryWriteRequest):
    return memory_backend.write(request.agent_id, request.protocol, request.payload)

@router.get("/memory/query", response_model=MemoryQueryResponse)
async def query_memory(
    key: str = Query(..., description="The semantic concept name (e.g., 'fullname')"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID")
):
    result = memory_backend.query(key, agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Fact not found in memory.")
    return result

