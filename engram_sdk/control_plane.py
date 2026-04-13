from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable, Tuple, TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from .client import EngramSDK

from .scope import Scope

logger = structlog.get_logger(__name__)

class ControlPlane:
    """
    Acts as the central state machine and enforces Programmatic Governed Inference (PGI).
    
    The ControlPlane owns the workflow sequence for data collection. It ensures 
    the model never decides the order of steps or data gathering, enforcing 
    strict sequencing so each piece of info is collected at the exact right moment.
    """
    
    def __init__(self, sdk: EngramSDK):
        self.sdk = sdk
        self.steps: Dict[str, Dict[str, Any]] = {}
        self.context: Dict[str, Any] = {}
        self.current_step_name: Optional[str] = None

    def add_step(
        self, 
        name: str, 
        tools: List[str], 
        handler: Optional[Callable[[Any, Dict[str, Any]], Tuple[Optional[str], Any]]] = None,
        required_fields: Optional[List[str]] = None,
        next_step: Optional[str] = None,
        description: Optional[str] = None
    ) -> ControlPlane:
        """
        Adds a governed data collection step to the state machine.
        
        Args:
            name: Unique ID for this step.
            tools: List of tool names allowed during this step.
            handler: Optional thick function for custom logic. 
                    Signature: (model_output, context) -> (next_step, data).
            required_fields: Optional list of keys that MUST be present in 
                            the model's JSON output for this step to succeed.
            next_step: Default transition if no handler is provided.
            description: Metadata about the data being gathered.
        """
        self.steps[name] = {
            "tools": tools,
            "handler": handler,
            "required_fields": required_fields,
            "next_step": next_step,
            "description": description
        }
        return self

    def run(
        self, 
        initial_step: str, 
        initial_data: Any, 
        inference_fn: Callable[[str, Scope, Any], Any]
    ) -> Any:
        """
        Executes the governed sequence starting from the initial step.
        """
        self.current_step_name = initial_step
        current_data = initial_data
        
        logger.info("starting_governed_sequence", initial_step=initial_step)
        
        while self.current_step_name:
            step_config = self.steps.get(self.current_step_name)
            if not step_config:
                raise ValueError(f"Step '{self.current_step_name}' not defined.")
            
            # 1. Enforce Tool Governance (Narrow Scope)
            step_scope = Scope(
                tools=step_config["tools"], 
                step_id=f"pgi_{self.current_step_name}_{self.sdk.agent_id or 'anon'}"
            )
            step_scope._sdk = self.sdk
            
            logger.info("collecting_data", step=self.current_step_name, tools=step_config["tools"])
            
            with step_scope:
                # 2. Governed Inference
                model_output = inference_fn(self.current_step_name, step_scope, current_data)
                
                # 3. Strict Sequence Validation
                # If required_fields are missing, we force a retry or prevent transition.
                if step_config["required_fields"]:
                    if not isinstance(model_output, dict):
                        raise ValueError(f"Step '{self.current_step_name}' expected dict output, got {type(model_output)}")
                    
                    missing = [f for f in step_config["required_fields"] if f not in model_output]
                    if missing:
                        logger.warning("missing_required_data", step=self.current_step_name, missing=missing)
                        # In a real system, you might trigger a 'retry_step' or error out.
                        # For now, we enforce strict compliance.
                        raise ValueError(f"Strict sequencing violation: Step '{self.current_step_name}' failed to collect {missing}")

                # 4. Programmatic Transition
                # Handler takes precedence, then default next_step.
                handler = step_config["handler"]
                if handler:
                    next_step, next_data = handler(model_output, self.context)
                else:
                    next_step = step_config["next_step"]
                    next_data = model_output
                
                logger.info(
                    "transitioning", 
                    from_step=self.current_step_name, 
                    to_step=next_step
                )
                
                self.current_step_name = next_step
                current_data = next_data

        return current_data
