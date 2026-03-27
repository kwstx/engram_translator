import structlog
import multiprocessing
from typing import Any, Dict, Callable, Optional
from app.core.config import settings

logger = structlog.get_logger(__name__)

class SandboxError(Exception):
    """Exception raised when code execution in the sandbox fails."""
    pass

class SafeExecutor:
    """
    Provides a sandboxed execution environment for agent logic or dynamic mapping rules.
    Prevents cross-invocation state pollution and limits resource usage.
    """

    @staticmethod
    def run_in_sandbox(func: Callable, args: tuple = (), kwargs: dict = {}, timeout: float = 5.0) -> Any:
        """
        Executes a function in a separate process with a timeout to enforce isolation.
        """
        if not settings.SANDBOX_ENABLED:
            logger.warning("Sandbox disabled. Executing in main process (insecure!)")
            return func(*args, **kwargs)

        # In a real-world scenario, we'd use a container (Docker) or a more robust
        # library like 'restrictedpython' or 'firejail'.
        # For this bridge, we'll use a isolated process with a timeout as a first layer.
        
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()

        def wrapper(q, f, a, kw):
            try:
                # Potentially apply more restrictions here (os.chroot, resource.setrlimit etc.)
                result = f(*a, **kw)
                q.put(("success", result))
            except Exception as e:
                q.put(("error", str(e)))

        process = ctx.Process(target=wrapper, args=(queue, func, args, kwargs))
        process.start()
        
        try:
            status, result = queue.get(timeout=timeout)
            process.join(timeout=1.0)
            if status == "success":
                return result
            raise SandboxError(result)
        except multiprocessing.TimeoutError:
            process.terminate()
            logger.error("Sandbox execution timed out", function=func.__name__)
            raise SandboxError("Execution timed out. Sandbox terminated.")
        except Exception as e:
            process.terminate()
            logger.error("Sandbox execution failed", error=str(e))
            raise SandboxError(f"Sandbox error: {str(e)}")
        finally:
            if process.is_alive():
                process.kill()

    @staticmethod
    def validate_rules(rules: list) -> bool:
        """
        Validates that dynamic logic rules (e.g. for PyDatalog) don't contain 
        forbidden patterns.
        """
        # Basic static analysis to prevent imports or dangerous builtins
        forbidden = ["import ", "eval(", "exec(", "os.", "subprocess.", "__"]
        for rule in rules:
            if any(f in str(rule) for f in forbidden):
                return False
        return True
