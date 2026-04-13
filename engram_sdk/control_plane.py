from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable, Tuple, TYPE_CHECKING
import structlog
import contextlib

if TYPE_CHECKING:
    from .client import EngramSDK

from .scope import Scope
from .global_data import get_global_data, GlobalData

logger = structlog.get_logger(__name__)

from .types import ToolCall
from .routing import RoutingEngine

class Step:
    """
    Defines a narrow list of allowed tools or functions for a specific moment 
    in the workflow, along with preconditions that must be satisfied and 
    transitions to the next step.
    
    NOTE: This is the RECOMMENDED pattern for production governed agents.
    Using Steps within a ControlPlane ensures deterministic, PGI-compliant 
    orchestration.
    """
    def __init__(
        self,
        name: str,
        tools: List[str],
        next_step: Optional[str] = None,
        preconditions: Optional[List[str]] = None,
        handler: Optional[Callable[[Any, GlobalData], Tuple[Optional[str], Any]]] = None,
        required_fields: Optional[List[str]] = None,
        description: Optional[str] = None,
        role_guidance: Optional[str] = None
    ):
        self.name = name
        self.tools = tools
        self.next_step = next_step
        self.preconditions = preconditions or []
        self.handler = handler
        self.required_fields = required_fields or []
        self.description = description
        self.role_guidance = role_guidance
        self.routing_decisions: Dict[str, str] = {}

    def setup(self, sdk: EngramSDK, routing_engine: RoutingEngine) -> Scope:
        """
        Activates the step by pre-calculating routing decisions and setting up the scope.
        """
        logger.info("step_activation_init", step=self.name, allowed_tools=self.tools)
        
        # 1. Evaluate performance-weighted graph and cache decisions
        self.routing_decisions = routing_engine.setup_step(self.name, self.tools)
        logger.info("routing_decisions_cached", step=self.name, decisions=self.routing_decisions)
        
        # 2. Initialize Scope with cached decisions
        scope = sdk.scope(self.name, tools=self.tools)
        scope.routing_decisions = self.routing_decisions
        return scope

    def validate_preconditions(self, data_store: GlobalData) -> bool:
        """Verifies that all required context from prior steps is satisfied."""
        missing = [p for p in self.preconditions if data_store.get(p) is None]
        if missing:
            logger.error("step_precondition_failed", step=self.name, missing=missing)
            return False
        return True

STANDARD_ROLE_GUIDANCE = (
    "You are a specialized agent participating in a governed tool-use workflow. "
    "Execute the provided tools to satisfy the current turn's objective. "
    "Decision-making regarding the overall sequence, data flow, and workflow "
    "transitions is handled by the ControlPlane. Do not attempt to plan or "
    "sequence subsequent steps."
)

class ControlPlane:
    """
    Acts as the central state machine and enforces Programmatic Governed Inference (PGI).
    
    The ControlPlane owns the workflow sequence for data collection. It ensures 
    the model never decides the order of steps or data gathering, enforcing 
    strict sequencing so each piece of info is collected at the exact right moment.
    
    NOTE: This is the RECOMMENDED production pattern for high-reliability agents.
    Retain the original full-registry behavior only for quick prototyping or 
    loose ambient mode (single-step agents).
    """
    
    def __init__(self, sdk: EngramSDK):
        self.sdk = sdk
        self.steps: Dict[str, Step] = {}
        self.global_data = get_global_data()
        self.current_step_name: Optional[str] = None
        self.tool_handlers: Dict[str, Callable] = {}
        self.role_guidance: str = STANDARD_ROLE_GUIDANCE
        self.routing_engine = RoutingEngine(sdk)

    def register_tool_handler(self, tool_name: str, handler: Callable) -> ControlPlane:
        """Maps a tool name to its local implementation function."""
        self.tool_handlers[tool_name] = handler
        return self

    def reset_global_data(self) -> None:
        """Clears all data from the global store."""
        self.global_data.clear()

    def add_step(
        self, 
        name: str, 
        tools: List[str], 
        handler: Optional[Callable[[Any, GlobalData], Tuple[Optional[str], Any]]] = None,
        required_fields: Optional[List[str]] = None,
        next_step: Optional[str] = None,
        preconditions: Optional[List[str]] = None,
        description: Optional[str] = None,
        role_guidance: Optional[str] = None
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
            next_step: Default transition if no handler is provided or if it returns it.
            preconditions: List of context keys that must exist before this step starts.
            description: Metadata about the data being gathered.
            role_guidance: Optional custom thin instruction for this specific step.
        """
        self.steps[name] = Step(
            name=name,
            tools=tools,
            handler=handler,
            required_fields=required_fields,
            next_step=next_step,
            preconditions=preconditions,
            description=description,
            role_guidance=role_guidance
        )
        return self

    def get_system_prompt(self, step_name: str) -> str:
        """
        Generates an extremely thin system prompt for the current step.
        Contains only basic role guidance and the current step's description.
        All sequencing logic remains strictly in the ControlPlane.
        """
        step = self.steps.get(step_name)
        guidance = (step.role_guidance if step and step.role_guidance 
                    else self.role_guidance)
        
        prompt = f"{guidance}\n\n"
        if step and step.description:
            prompt += f"CURRENT OBJECTIVE: {step.description}\n"
        
        return prompt.strip()

    def run(
        self, 
        initial_step: str, 
        initial_data: Any, 
        inference_fn: Callable[[str, Scope, Any, str], Any]
    ) -> Any:
        """
        Executes the governed sequence starting from the initial step.
        """
        self.current_step_name = initial_step
        current_data = initial_data
        
        logger.info("governed_sequence_started", initial_step=initial_step)
        
        while self.current_step_name:
            step = self.steps.get(self.current_step_name)
            if not step:
                logger.error("step_not_found", step_name=self.current_step_name)
                raise ValueError(f"Step '{self.current_step_name}' not defined.")
            
            # 1. Enforce Preconditions
            logger.info("validating_preconditions", step=self.current_step_name, required=step.preconditions)
            if not step.validate_preconditions(self.global_data):
                missing = [p for p in step.preconditions if self.global_data.get(p) is None]
                logger.error("precondition_failure", step=self.current_step_name, missing=missing)
                raise ValueError(f"Step '{self.current_step_name}' failed preconditions. Missing: {missing}")

            # 2. Step Setup & Routing Evaluation (Activation Time)
            step_scope = step.setup(self.sdk, self.routing_engine)
            step_scope._sdk = self.sdk
            
            with step_scope:
                # 3. Governed Inference (Thin Prompt)
                system_prompt = self.get_system_prompt(self.current_step_name)
                logger.info("governed_inference_start", step=self.current_step_name, prompt_len=len(system_prompt))
                
                model_output = inference_fn(
                    self.current_step_name, 
                    step_scope, 
                    current_data, 
                    system_prompt
                )
                
                logger.info("governed_inference_complete", step=self.current_step_name, output_type=type(model_output).__name__)
                
                # 4. Strict Sequence Validation
                if step.required_fields:
                    logger.info("validating_required_data", step=self.current_step_name, keys=step.required_fields)
                    if not isinstance(model_output, dict):
                        logger.error("output_format_error", step=self.current_step_name, expected="dict", got=type(model_output).__name__)
                        raise ValueError(f"Step '{self.current_step_name}' expected dict output, got {type(model_output)}")
                    
                    missing = [f for f in step.required_fields if f not in model_output]
                    if missing:
                        logger.warning("strict_sequencing_violation", step=self.current_step_name, missing=missing)
                        raise ValueError(f"Strict sequencing violation: Step '{self.current_step_name}' failed to collect {missing}")
                    logger.info("required_data_validated", step=self.current_step_name)

                # 5. Programmatic Transition
                if step.handler:
                    logger.info("executing_step_handler", step=self.current_step_name)
                    next_step, next_data = step.handler(model_output, self.global_data)
                else:
                    next_step = step.next_step
                    next_data = model_output
                
                logger.info(
                    "step_transition", 
                    from_step=self.current_step_name, 
                    to_step=next_step
                )
                
                self.current_step_name = next_step
                current_data = next_data

        logger.info("governed_sequence_complete")
        return current_data

    def drive(
        self, 
        initial_step: str, 
        inference_fn: Callable[[str, Scope, str], ToolCall]
    ) -> Any:
        """
        Strict Orchestrator: Drives the governed workflow turn-by-turn.
        
        For each step:
        1. Activates the current Step and enforces preconditions.
        2. Supplies ONLY validated tools for that Step to the model via Scope.
        3. Executes the chosen tool and writes results to GlobalData.
        4. Automatically advances to the next Step.
        """
        self.current_step_name = initial_step
        
        logger.info("orchestrator_session_started", initial_step=initial_step)
        
        while self.current_step_name:
            step = self.steps.get(self.current_step_name)
            if not step:
                logger.error("step_not_found", step_name=self.current_step_name)
                raise ValueError(f"Step '{self.current_step_name}' not defined.")
            
            # 1. Enforce Preconditions
            logger.info("validating_preconditions", step=self.current_step_name, required=step.preconditions)
            if not step.validate_preconditions(self.global_data):
                missing = [p for p in step.preconditions if self.global_data.get(p) is None]
                logger.error("precondition_failure", step=self.current_step_name, missing=missing)
                raise ValueError(f"Step '{self.current_step_name}' failed preconditions. Missing: {missing}")

            # 2. Step Setup & Routing Evaluation (Activation Time)
            with step.setup(self.sdk, self.routing_engine) as scope:
                logger.info("orchestrator_step_active", step=step.name, allowed_tools=step.tools)
                
                # Call model with Thin Prompt role guidance
                system_prompt = self.get_system_prompt(self.current_step_name)
                logger.info("orchestrator_inference_start", step=self.current_step_name)
                
                tool_call = inference_fn(self.current_step_name, scope, system_prompt)
                
                logger.info("orchestrator_tool_proposal", step=step.name, tool=tool_call.name)

                # Governance Check: Did the model call a permitted tool?
                if tool_call.name not in step.tools:
                    logger.error("governance_violation", step=step.name, attempted_tool=tool_call.name, allowed=step.tools)
                    raise ValueError(f"Step '{step.name}' violation: Tool '{tool_call.name}' is not allowed.")
                
                logger.info("governance_check_passed", step=step.name, tool=tool_call.name)

                # 3. Execute Tool
                handler = self.tool_handlers.get(tool_call.name)
                if not handler:
                    logger.error("tool_handler_missing", tool=tool_call.name)
                    raise ValueError(f"No handler registered for tool '{tool_call.name}'")

                logger.info("executing_governed_tool", tool=tool_call.name, arguments=list(tool_call.arguments.keys()))
                result = handler(**tool_call.arguments)
                logger.info("tool_execution_complete", tool=tool_call.name, result_type=type(result).__name__)
                
                # 4. Write Results to GlobalData
                # Store the raw return value in a step-specific key
                result_key = f"{step.name}_output"
                logger.info("writing_to_global_data", key=result_key, step=step.name)
                self.global_data.set(result_key, result)
                
                # 5. Programmatic Transition
                if step.handler:
                    logger.info("executing_step_handler", step=step.name)
                    next_step, _ = step.handler(result, self.global_data)
                else:
                    # Default to predefined next_step
                    next_step = step.next_step
                
                logger.info("orchestrator_step_transition", from_step=step.name, to_step=next_step)
                self.current_step_name = next_step
                
        logger.info("orchestrator_session_finished")
        return self.global_data.all()

    @contextlib.contextmanager
    def step(self, name: str):
        """
        SDK Context manager for entering a governed step.
        
        This manages scope activation, drift validation, and routing pre-calculation 
        automatically. It ensures that only tools permitted for this specific step 
        are available to the model.
        
        Example:
            with cp.step("data_gathering"):
                # calls tool...
        """
        logger.info("entering_governed_step", step_name=name)
        step = self.steps.get(name)
        if not step:
            # Fallback for ad-hoc steps or remote steps not yet registered locally
            # This enables the 'loose ambient mode' for quick prototyping.
            logger.info("loose_ambient_mode_active", step_name=name)
            scope = self.sdk.scope(name)
        else:
            # Full governed activation
            logger.info("validating_preconditions", step=name, required=step.preconditions)
            if not step.validate_preconditions(self.global_data):
                missing = [p for p in step.preconditions if self.global_data.get(p) is None]
                logger.error("precondition_failure", step=name, missing=missing)
                raise ValueError(f"Step '{name}' failed preconditions. Missing: {missing}")
            
            scope = step.setup(self.sdk, self.routing_engine)
        
        with scope as activated_scope:
            self.current_step_name = name
            yield activated_scope
        
        logger.info("exiting_governed_step", step_name=name)

    def flow(self, name: str) -> ControlPlane:
        """
        Enters the context of a specific named flow.
        
        This method retrieves the flow definition (sequence of steps) from the 
        registry and can be used to initialize the ControlPlane sequence.
        """
        logger.info("entering_flow", flow_name=name)
        try:
            flow_steps = self.sdk.transport.request_json("GET", f"/registry/flow/{name}")
            # For now, we just ensure these steps are 'known' or log the sequence.
            # In a more advanced version, this could pre-validate the whole sequence.
            logger.debug("flow_steps_resolved", count=len(flow_steps))
        except Exception as e:
            logger.warning("flow_resolution_failed", flow_name=name, error=str(e))
        
        return self
