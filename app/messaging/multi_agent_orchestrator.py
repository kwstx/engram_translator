import asyncio
import uuid
import re
import time
from datetime import datetime, timezone
import structlog
from typing import List, Dict, Any, Optional, Tuple
from app.messaging.orchestrator import Orchestrator, HandoffResult
from app.core.exceptions import (
    HandoffAuthorizationError, 
    TranslationError,
    TransientError,
    PermanentError,
    RateLimitError,
    NetworkError,
    ExpiredTokenError,
    InvalidCredentialsError
)
from app.core.security import verify_engram_token
from app.messaging.connectors.registry import get_default_registry
from bridge.memory import memory_backend
from app.core.tui_bridge import tui_event_queue
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.models import PermissionProfile
from app.core.metrics import record_connector_call, record_task_completion, record_task_start
from app.core.logging import bind_context

logger = structlog.get_logger(__name__)

class MultiAgentOrchestrator:
    """
    Advanced Orchestration Layer for multi-agent coordination.
    Handles task parsing, agent selection, permission verification (EAT),
    sequential execution with dependency management, and result normalization.
    """
    def __init__(self, orchestrator: Optional[Orchestrator] = None):
        self.orchestrator = orchestrator or Orchestrator()
        self.connector_registry = get_default_registry()

    async def execute_task(
        self, 
        user_task: str, 
        eat: str, 
        db: Optional[AsyncSession] = None,
        task_id: Optional[uuid.UUID] = None,
        plan: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Coordinates a complex task across multiple agents.
        """
        from app.db.models import Task, TaskStatus # Local import to avoid cycles

        # 1. Verify EAT and extract user info
        try:
            auth_payload = verify_engram_token(eat)
            user_id = str(auth_payload.get("sub"))
            bind_context(user_id=user_id, task_id=str(task_id) if task_id else None)
            logger.info("Multi-agent task execution started", user_task=user_task)
        except Exception as e:
            logger.error("Authorization failed", error=str(e))
            raise HandoffAuthorizationError(f"Invalid or missing Engram Access Token (EAT): {str(e)}")

        # Update task status to RUNNING if task_id provided
        db_task = None
        if db and task_id:
            stmt = select(Task).where(Task.id == task_id)
            res = await db.execute(stmt)
            db_task = res.scalars().first()
            if db_task:
                db_task.status = TaskStatus.RUNNING
                db_task.updated_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(db_task)

        # 2. Parse Task into a Plan
        start_time = time.time()
        if not plan:
            plan = self._generate_plan(user_task)
        
        if not plan:
            logger.warning("Planner failed to generate plan")
            tui_event_queue.put_nowait(f"⚠️ [bold yellow]Planner:[/] Could not determine subtasks for '{user_task[:30]}...'")
            err_res = {
                "status": "error", 
                "message": "Task parser could not determine a multi-agent plan. Please name the agents (e.g., Claude, Perplexity, Slack) in your request."
            }
            if db_task:
                db_task.status = TaskStatus.DEAD_LETTER
                db_task.last_error = err_res["message"]
                await db.commit()
            return err_res

        logger.info("Orchestration plan generated", step_count=len(plan))
        tui_event_queue.put_nowait(f"📋 [bold cyan]Orchestration Plan:[/] Split into {len(plan)} agent steps.")

        results = {}
        context = {"original_task": user_task}
        correlation_id = str(uuid.uuid4())

        # 4. Execution Loop
        max_retries = 3
        for i, step in enumerate(plan):
            agent_name = step["agent"].upper()
            sub_command = step["command"]
            
            # Simple context injection
            for prev_agent, prev_res in results.items():
                pattern = f"\\{{{prev_agent}\\}}"
                if re.search(pattern, sub_command, re.IGNORECASE):
                    injection_content = prev_res.get("content") or prev_res.get("summary") or prev_res.get("result") or str(prev_res)
                    sub_command = re.sub(pattern, str(injection_content), sub_command, flags=re.IGNORECASE)

            # Execution with Retries
            last_err = None
            for attempt in range(max_retries):
                logger.info("Executing step", step_index=i+1, agent=agent_name, attempt=attempt+1)
                tui_event_queue.put_nowait(f"🔄 [yellow]Step {i+1} (Att {attempt+1}):[/] Handing off to [bold]{agent_name}[/]")
                step_start_time = time.time()
                try:
                    # Permission check
                    if db:
                        await self._verify_db_permissions(db, user_id, agent_name, auth_payload)
                    else:
                        self._verify_eat_scopes(auth_payload, agent_name)

                    source_message = {
                        "command": sub_command,
                        "metadata": {
                            "correlation_id": correlation_id,
                            "step": i + 1,
                            "total_steps": len(plan),
                            "orchestrator": "MultiAgentOrchestrator/v1",
                            "attempt": attempt + 1
                        }
                    }
                    
                    handoff_res = await self.orchestrator.handoff_async(
                        source_message=source_message,
                        source_protocol="NL",
                        target_protocol=agent_name,
                        eat=eat,
                        db=db
                    )
                    
                    step_result = handoff_res.translated_message
                    
                    if isinstance(step_result, dict) and step_result.get("status") == "error":
                        err_type = step_result.get("error_type", "")
                        is_transient = step_result.get("is_transient", False)
                        
                        record_connector_call(agent_name, user_id, "error", time.time() - step_start_time)
                        
                        if "ExpiredToken" in err_type:
                            raise ExpiredTokenError(step_result.get("detail", "Token expired"))
                        if "InvalidCredentials" in err_type:
                            raise InvalidCredentialsError(step_result.get("detail", "Invalid credentials"))
                        
                        if is_transient or "RateLimit" in err_type or "Network" in err_type:
                            raise NetworkError(step_result.get("detail", "Transient tool error"))
                            
                        raise TranslationError(step_result.get("detail", "Permanent agent execution error"))

                    record_connector_call(agent_name, user_id, "success", time.time() - step_start_time)
                    results[agent_name] = step_result
                    context[f"step_{i}_result"] = step_result
                    
                    # Record to Swarm Memory
                    memory_backend.write(
                        agent_id="Orchestrator",
                        protocol="A2A",
                        payload={
                            "correlation_id": correlation_id,
                            "step": i,
                            "agent": agent_name,
                            "status": "completed"
                        }
                    )
                    
                    logger.info("Step completed", step_index=i+1, agent=agent_name)
                    tui_event_queue.put_nowait(f"✅ [green]Step {i+1} OK:[/] [bold]{agent_name}[/] finished.")
                    
                    if db and db_task:
                        if not db_task.results:
                            db_task.results = {}
                        db_task.results[agent_name] = step_result
                        db_task.updated_at = datetime.now(timezone.utc)
                        await db.commit()
                        await db.refresh(db_task)

                    last_err = None
                    break # Success!

                except ExpiredTokenError as e:
                    logger.warning("Step auth error: token expired", agent=agent_name, error=str(e))
                    tui_event_queue.put_nowait(f"🔑 [bold red]Auth Error:[/] Token for {agent_name} expired. Please refresh credentials.")
                    return {"status": "error", "error": "token_expired", "action_required": "REFRESH_CREDENTIALS", "detail": str(e)}
                
                except InvalidCredentialsError as e:
                    logger.warning("Step auth error: invalid credentials", agent=agent_name, error=str(e))
                    tui_event_queue.put_nowait(f"🚫 [bold red]Auth Error:[/] Invalid credentials for {agent_name}.")
                    return {"status": "error", "error": "invalid_credentials", "detail": str(e)}

                except (TransientError, NetworkError, RateLimitError) as e:
                    last_err = e
                    logger.warning("Step transient failure", agent=agent_name, attempt=attempt+1, error=str(e))
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 * (attempt + 1)) # Backoff
                    else:
                        logger.error("Step failed after retries", agent=agent_name, error=str(e))
                        tui_event_queue.put_nowait(f"⏳ [red]Step {i+1} failed after retries:[/] {agent_name} is currently unavailable.")
                
                except Exception as e:
                    logger.error("Step permanent failure", agent=agent_name, error=str(e), exc_info=True)
                    tui_event_queue.put_nowait(f"❌ [red]Orchestration aborted at {agent_name}:[/] Permanent error: {str(e)}")
                    err_data = {
                        "status": "error",
                        "failed_step": i + 1,
                        "failed_agent": agent_name,
                        "error": str(e),
                        "partial_results": results
                    }
                    if db and db_task:
                        db_task.status = TaskStatus.DEAD_LETTER
                        db_task.last_error = str(e)
                        db_task.results = results
                        db_task.updated_at = datetime.now(timezone.utc)
                        await db.commit()
                    return err_data
            
            if last_err:
                err_data = {
                    "status": "error",
                    "failed_step": i + 1,
                    "failed_agent": agent_name,
                    "error": str(last_err),
                    "partial_results": results
                }
                if db and db_task:
                    db_task.status = TaskStatus.DEAD_LETTER
                    db_task.last_error = str(last_err)
                    db_task.results = results
                    await db.commit()
                return err_data

        # 5. Merge and Normalize Output
        final_summary = self._normalize_final_output(results, user_task)
        logger.info("Multi-agent task completed successfully", agents_involved=list(results.keys()))
        tui_event_queue.put_nowait(f"🏁 [bold green]Complex task synchronized successfully.[/]")
        
        final_res = {
            "status": "success",
            "correlation_id": correlation_id,
            "results": results,
            "normalized_output": final_summary
        }

        if db and db_task:
            db_task.status = TaskStatus.COMPLETED
            db_task.results = results
            db_task.completed_at = datetime.now(timezone.utc)
            db_task.updated_at = datetime.now(timezone.utc)
            await db.commit()

        return final_res

    def _generate_plan(self, task: str) -> List[Dict[str, Any]]:
        """
        Parses the natural language task into a plan of agent calls.
        """
        plan = []
        known_agents = self.connector_registry.list_connectors()
        steps = re.split(r"[,;] then | then | and then |; |finally ", task, flags=re.IGNORECASE)
        
        for step_text in steps:
            step_text = step_text.strip()
            if not step_text: continue
            
            target_agent = None
            for agent in known_agents:
                if agent.lower() in step_text.lower():
                    target_agent = agent
                    break
            
            if not target_agent and ("post" in step_text.lower() or "send" in step_text.lower()):
                if "SLACK" in known_agents:
                    target_agent = "SLACK"
            
            if not target_agent and ("search" in step_text.lower() or "research" in step_text.lower()):
                if "PERPLEXITY" in known_agents:
                    target_agent = "PERPLEXITY"

            if target_agent:
                plan.append({
                    "agent": target_agent,
                    "command": step_text
                })
        
        if not plan:
            for agent in known_agents:
                if agent.lower() in task.lower():
                    plan.append({"agent": agent, "command": task})
                    
        return plan

    async def _verify_db_permissions(self, db: AsyncSession, user_id: str, agent_name: str, payload: Dict[str, Any]):
        """Checks both EAT scopes and database PermissionProfile."""
        try:
            self._verify_eat_scopes(payload, agent_name)
            return
        except HandoffAuthorizationError:
            pass
            
        try:
            stmt = select(PermissionProfile).where(PermissionProfile.user_id == uuid.UUID(user_id))
            res = await db.execute(stmt)
            profile = res.scalars().first()
            
            if not profile:
                raise HandoffAuthorizationError(f"No permission profile found for user {user_id}")
                
            perms = profile.permissions or {}
            if "*" in perms or agent_name.upper() in [k.upper() for k in perms.keys()]:
                return
                
            raise HandoffAuthorizationError(f"User profile does not permit access to agent '{agent_name}'")
        except ValueError:
             raise HandoffAuthorizationError(f"Invalid user_id in EAT: {user_id}")

    def _verify_eat_scopes(self, payload: Dict[str, Any], agent_name: str):
        allowed_tools = payload.get("allowed_tools", [])
        scopes = payload.get("scopes", {})
        agent_key = agent_name.upper()
        
        if "*" in allowed_tools:
            return
            
        if "translator" in allowed_tools:
            t_scopes = scopes.get("translator", [])
            if "*" in t_scopes or agent_key in t_scopes:
                return

        if agent_key in [t.upper() for t in allowed_tools]:
            return
            
        raise HandoffAuthorizationError(f"EAT does not authorize access to tool '{agent_name}'")

    def _normalize_final_output(self, results: Dict[str, Any], original_task: str) -> Dict[str, Any]:
        """Merges results into a single cohesive response."""
        full_text = ""
        for agent, res in results.items():
            content = res.get("content") or res.get("summary") or res.get("result") or str(res)
            full_text += f"### {agent} Response\n{content}\n\n"
            
        return {
            "task_summary": f"Executed multi-agent orchestration for: {original_task}",
            "full_report": full_text.strip(),
            "completion_status": "Success",
            "agents_involved": list(results.keys()),
            "timestamp": time.time()
        }
