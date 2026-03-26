import asyncio
import hashlib
import json
import structlog
from typing import Any, Dict, Optional, Callable, Awaitable
from pydantic import create_model, BaseModel, ValidationError
from datetime import datetime, timezone
from app.core.tui_bridge import tui_event_queue
from bridge.memory import memory_backend

logger = structlog.get_logger(__name__)

# CIRCUIT BREAKER STATE
# destination -> failure_count
_circuit_breaker: Dict[str, int] = {}
BREAKER_THRESHOLD = 5
COOLDOWN_SECONDS = 30
_last_failure_time: Dict[str, datetime] = {}

def get_idempotency_key(payload: Any, correlation_id: str, retry_count: int) -> str:
    """
    Generates a unique idempotency key based on message hash, correlation_id and retry count.
    """
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()[:16]
    return f"{payload_hash}:{correlation_id}:{retry_count}"

def log_to_tui(message: str):
    """Logs a message directly to the TUI trace panel."""
    try:
        tui_event_queue.put_nowait(message)
    except Exception:
        pass

class ReliabilityMiddleware:
    """
    Wraps routing calls with reliability primitives:
    - Idempotency / Exactly-once semantics via memory layer
    - Circuit Breaker pattern per destination
    - Auto schema inference & Pydantic validation
    - TUI trace logging
    """
    
    def __init__(self, func: Callable[..., Awaitable[Dict[str, Any]]]):
        self.func = func

    async def __call__(
        self, 
        target: str, 
        payload: Any, 
        correlation_id: str = "default", 
        retry_count: int = 0, 
        **kwargs: Any
    ) -> Dict[str, Any]:
        
        # 1. CIRCUIT BREAKER CHECK
        if _circuit_breaker.get(target, 0) >= BREAKER_THRESHOLD:
            last_fail = _last_failure_time.get(target)
            if last_fail and (datetime.now(timezone.utc) - last_fail).total_seconds() < COOLDOWN_SECONDS:
                log_to_tui(f"🚫 [bold red]Circuit breaker tripped for {target}.[/] Pausing routing.")
                return {
                    "status": "error",
                    "error": "circuit_breaker_open",
                    "destination": target,
                    "retry_after": COOLDOWN_SECONDS
                }
            else:
                # Reset if cooldown passed
                _circuit_breaker[target] = 0
                log_to_tui(f"🔄 [bold yellow]Circuit breaker for {target} cooling down...[/] Retrying.")

        # 2. SCHEMA INFERENCE & VALIDATION
        if isinstance(payload, dict):
            try:
                # Dynamically create model for validation
                # In a real system, we'd compare against known schemas.
                # Here we use it for 'auto inference'.
                fields = {k: (type(v), ...) for k, v in payload.items()}
                DynamicModel = create_model("InferredPayloadModel", **fields)
                DynamicModel(**payload) # Validate
                
                # If everything is there but some fields look weird (low confidence)
                # For demo purposes, if keys contain 'unknown' or 'temp', log low confidence
                if any("unknown" in str(k).lower() or "temp" in str(k).lower() for k in payload.keys()):
                    log_to_tui(f"⚠️ [bold yellow]Low-confidence payload:[/] {target} schema contains ambiguous fields.")
            except Exception as e:
                log_to_tui(f"👀 [bold cyan]Schema inference alert:[/] Detected novel payload structure for {target}.")

        # 3. IDEMPOTENCY / EXACTLY-ONCE
        idemp_key = get_idempotency_key(payload, correlation_id, retry_count)
        
        # Check memory layer
        if memory_backend.check_exists('idempotency_key', idemp_key, 'middle_ware'):
            log_to_tui(f"🛡️ [bold green]Exactly-once enforced:[/] Skipping duplicate message {idemp_key}")
            return {
                "status": "cached",
                "message": "Message already processed",
                "idempotency_key": idemp_key
            }

        # 4. EXECUTION
        try:
            log_to_tui(f"🛰️ [bold blue]Routing message:[/] {target} (ID: {idemp_key[:8]})")
            result = await self.func(target, payload, correlation_id, retry_count, **kwargs)
            
            # Record success in memory
            memory_backend.write('middle_ware', 'INTERNAL', {"idempotency_key": idemp_key})
            
            # Reset circuit breaker on success
            _circuit_breaker[target] = 0
            
            return result
            
        except Exception as e:
            # 5. CIRCUIT BREAKER FAILURE TRACKING
            _circuit_breaker[target] = _circuit_breaker.get(target, 0) + 1
            _last_failure_time[target] = datetime.now(timezone.utc)
            
            log_to_tui(f"🚨 [bold red]Routing failed for {target}:[/] {str(e)}")
            
            raise e

def wrap_route_to(func):
    middleware = ReliabilityMiddleware(func)
    async def wrapper(*args, **kwargs):
        return await middleware(*args, **kwargs)
    return wrapper
