import uuid
import time
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select
import structlog
from app.db.session import get_session
from app.core.security import get_current_principal, verify_engram_token
from app.core.semantic_auth import SemanticAuthorizationService
import subprocess
from app.db.models import ToolRegistry, ToolExecutionMetadata
from app.services.registry_service import RegistryService
from app.services.tool_routing import (
    available_backends,
    estimate_backend_stats,
    estimate_tokens,
    fetch_backend_stats,
    log_routing_decision,
    route_tool_backend_sync,
    finalize_routing_decision,
    MCP_BACKEND,
    HTTP_BACKEND,
    CLI_BACKEND,
)

router = APIRouter(prefix="/registry", tags=["Registry"])
logger = structlog.get_logger(__name__)

# --- Ingestion Endpoints ---

@router.post("/ingest/openapi", status_code=status.HTTP_201_CREATED)
async def ingest_openapi(
    url_or_path: str = Body(..., embed=True),
    agent_id: str = Body(..., embed=True),
    db: Session = Depends(get_session)
):
    """
    Ingests an OpenAPI spec and registers its tools.
    """
    service = RegistryService(db)
    agent_uuid = uuid.UUID(agent_id)
    tool = await service.ingest_openapi(url_or_path, agent_uuid)
    return tool

@router.post("/ingest/cli", status_code=status.HTTP_201_CREATED)
async def ingest_cli(
    command: str = Body(..., embed=True),
    agent_id: str = Body(..., embed=True),
    db: Session = Depends(get_session)
):
    """
    Ingests a CLI tool by parsing its --help output.
    """
    service = RegistryService(db)
    agent_uuid = uuid.UUID(agent_id)
    tool = await service.ingest_cli_help(command, agent_uuid)
    return tool

@router.get("/tools")
async def list_tools(db: Session = Depends(get_session)):
    """
    List all registered tools.
    """
    tools = db.exec(select(ToolRegistry)).all()
    return tools

# --- MCP Native Server Implementation (JSON-RPC over HTTP) ---

@router.post("/mcp/call", response_model=Dict[str, Any])
async def call_mcp_tool(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal)
):
    """
    Implement JSON-RPC 2.0 to call a registered tool.
    Discovery + Execution for agents.
    """
    # JSON-RPC Handling
    method = request.get("method")
    params = request.get("params", {})
    jsonrpc_id = request.get("id")

    if method == "mcp.list_tools":
        tools = db.exec(select(ToolRegistry)).all()
        result = [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "actions": t.actions or [],
                "input_schema": t.input_schema or {}
            }
            for t in tools
        ]
        return {"jsonrpc": "2.0", "id": jsonrpc_id, "result": {"tools": result}}

    if method == "mcp.call_tool":
        tool_id = params.get("tool_id")
        action_name = params.get("action")
        arguments = params.get("arguments", {})
        task_description = params.get("task_description") or params.get("task")

        tool = db.get(ToolRegistry, uuid.UUID(tool_id))
        if not tool:
            return {"jsonrpc": "2.0", "id": jsonrpc_id, "error": {"code": -32601, "message": "Tool not found"}}

        # Determine execution path
        metadata = tool.execution_metadata
        if metadata:
            task_description = _infer_task_description(tool, action_name, arguments, task_description)
            backends = available_backends(tool, metadata)
            stats = await fetch_backend_stats(db, tool.id, backends)
            stats = {
                backend: estimate_backend_stats(tool, metadata, backend, task_description, stats.get(backend))
                for backend in backends
            }
            decision = route_tool_backend_sync(tool, metadata, task_description, stats)
            decision_record = await log_routing_decision(db, tool.id, action_name, decision)

            start = time.perf_counter()
            error_message = None
            try:
                if decision.backend == CLI_BACKEND:
                    result = await run_cli_execution(tool, metadata, action_name, arguments, principal)
                elif decision.backend in {MCP_BACKEND, HTTP_BACKEND}:
                    result = await run_http_execution(tool, metadata, action_name, arguments, principal)
                else:
                    result = await run_http_execution(tool, metadata, action_name, arguments, principal)
            except Exception as exc:
                error_message = str(exc)
                raise
            finally:
                latency_ms = (time.perf_counter() - start) * 1000.0
                token_cost_actual = _estimate_result_tokens(result if "result" in locals() else {"error": error_message})
                success = False
                if "result" in locals() and isinstance(result, dict):
                    if "error" in result:
                        success = False
                        error_message = error_message or result.get("error", {}).get("message")
                    elif "result" in result:
                        success = True
                await finalize_routing_decision(
                    db,
                    decision_record.id,
                    success=success,
                    latency_ms=latency_ms,
                    token_cost_actual=token_cost_actual,
                    error=error_message,
                )
            return result

        return {"jsonrpc": "2.0", "id": jsonrpc_id, "error": {"code": -32603, "message": "Execution type not supported yet"}}

    return {"jsonrpc": "2.0", "id": jsonrpc_id, "error": {"code": -32601, "message": "Method not found"}}


async def run_cli_execution(tool: ToolRegistry, metadata: ToolExecutionMetadata, action: str, args: Dict[str, Any], principal: Dict[str, Any]):
    """
    Execute a CLI command in a secure subprocess.
    """
    try:
        token = principal.get("_raw_token")
        if not token:
            return {"jsonrpc": "2.0", "error": {"code": -32001, "message": "Missing EAT token."}}
        payload = verify_engram_token(token)
        authz = SemanticAuthorizationService()
        args = authz.enforce(payload, tool, action, args)
    except HTTPException as exc:
        return {"jsonrpc": "2.0", "error": {"code": -32001, "message": exc.detail}}

    # CLI Command construction
    params = _exec_params(metadata)
    cmd_base = params.get("cli_command", tool.name)
    # Inject auth env vars from principal/EAT
    env = {"ENGRAM_EAT": principal.get("_raw_token")}
    
    # Secure subprocess call (Using docker if available, fallback to direct in sandbox)
    try:
        # Mock/Simplified isolated run
        # In production, this would use a Docker SDK to spin up a container
        full_args = [f"--{k}={v}" for k,v in args.items()]
        result = subprocess.run([cmd_base] + full_args, capture_output=True, text=True, env=env)
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        }
    except Exception as e:
        return {"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}

async def run_http_execution(tool: ToolRegistry, metadata: ToolExecutionMetadata, action: str, args: Dict[str, Any], principal: Dict[str, Any]):
    try:
        token = principal.get("_raw_token")
        if not token:
            return {"jsonrpc": "2.0", "error": {"code": -32001, "message": "Missing EAT token."}}
        payload = verify_engram_token(token)
        authz = SemanticAuthorizationService()
        _ = authz.enforce(payload, tool, action, args)
    except HTTPException as exc:
        return {"jsonrpc": "2.0", "error": {"code": -32001, "message": exc.detail}}
    # HTTP orchestration
    return {"jsonrpc": "2.0", "result": {"message": "HTTP tool call routed (mock result)"}}


def _exec_params(metadata: ToolExecutionMetadata) -> Dict[str, Any]:
    if getattr(metadata, "exec_params", None):
        return metadata.exec_params or {}
    if getattr(metadata, "metadata", None):
        return metadata.metadata or {}
    return {}


def _infer_task_description(
    tool: ToolRegistry,
    action_name: Optional[str],
    arguments: Dict[str, Any],
    provided: Optional[str],
) -> str:
    if provided:
        return provided
    parts = [tool.name, tool.description]
    if action_name:
        parts.append(f"Action: {action_name}")
    if arguments:
        parts.append(f"Args: {json.dumps(arguments)}")
    return " | ".join([p for p in parts if p])


def _estimate_result_tokens(result: Dict[str, Any]) -> int:
    try:
        payload = json.dumps(result)
    except Exception:
        payload = str(result)
    return estimate_tokens(payload)

# --- Helper to register the router ---
# Usually done in main.py
