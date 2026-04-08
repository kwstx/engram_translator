# Reliability Middleware

The reliability middleware wraps every routing call with circuit breakers, retry logic, idempotency enforcement, and dynamic schema validation. This ensures that tool executions are robust, recoverable, and exactly-once — even when downstream APIs are flaky.

---

## Overview

The `ReliabilityMiddleware` class (`reliability/middleware.py`) sits between the routing engine and actual tool execution:

```
Routing Decision → ReliabilityMiddleware → Tool Execution → Response Validation → Trace Recording
```

Every call through the middleware is:
- **Retried** on transient failures with exponential backoff
- **Circuit-broken** per destination — if a tool consistently fails, the circuit opens and prevents further calls until cooldown completes
- **Deduplicated** via idempotency keys — the same request won't execute twice
- **Validated** against a dynamically inferred schema — responses are checked for structural correctness

---

## Circuit Breaker

### How It Works

Each tool/backend destination has its own circuit breaker state:

| State | Behavior |
|---|---|
| **CLOSED** | Normal operation — all requests pass through |
| **OPEN** | Requests are immediately rejected. No calls to the backend. |
| **HALF-OPEN** | A single probe request is allowed. If it succeeds, circuit closes. If it fails, circuit reopens. |

### Configuration

The circuit breaker is configured per-instance:

| Parameter | Default | Description |
|---|---|---|
| **Failure threshold** | 5 | Number of consecutive failures before opening |
| **Cooldown period** | 30 seconds | How long the circuit stays open before transitioning to half-open |
| **Success threshold** | 1 | Number of successes in half-open before closing |

### State Tracking

```python
# From reliability/middleware.py
class CircuitBreaker:
    async def check_circuit(self, destination: str) -> bool:
        """Returns True if the circuit is closed (requests allowed)."""
        state = self._get_state(destination)
        if state == "OPEN":
            if time.time() - state.opened_at > self.cooldown:
                return True  # Transition to HALF-OPEN
            return False  # Still in cooldown
        return True  # CLOSED or HALF-OPEN

    async def record_success(self, destination: str): ...
    async def record_failure(self, destination: str): ...
```

### TUI Integration

When a circuit breaker trips, the event is emitted to the TUI trace panel:

```
⚡ Circuit breaker OPENED for destination: Slack-MCP (5 consecutive failures)
🔄 Circuit breaker HALF-OPEN for destination: Slack-MCP (cooldown expired)
✅ Circuit breaker CLOSED for destination: Slack-MCP (probe succeeded)
```

---

## Retry Logic

Retries use `tenacity` with exponential backoff:

```python
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
)
async def execute_with_retry(self, ...):
    ...
```

| Parameter | Value | Description |
|---|---|---|
| **Max attempts** | 3 | Total attempts including the initial try |
| **Min wait** | 1 second | Minimum backoff duration |
| **Max wait** | 60 seconds | Maximum backoff duration |
| **Multiplier** | 1 | Exponential multiplier |
| **Retryable errors** | Connect, Timeout | Only transient errors are retried |

Non-retryable errors (400 Bad Request, 403 Forbidden, 404 Not Found) fail immediately without retry.

---

## Idempotency

Every request through the middleware is assigned an idempotency key:

```python
# Generate idempotency key from payload
idempotency_key = hashlib.sha256(
    json.dumps(payload, sort_keys=True).encode()
).hexdigest()
```

### How It Works

1. Before execution, the middleware checks if this `idempotency_key` has been seen before
2. If found in Redis (or in-memory cache), the stored result is returned immediately
3. If not found, the request proceeds and the result is stored with the key
4. Idempotency keys expire after a configurable TTL

### Correlation IDs

Each request also gets a unique `correlation_id` for trace linkage:

```python
correlation_id = str(uuid.uuid4())
```

This ensures that retries of the same logical request can be grouped in traces.

---

## Dynamic Schema Validation

The middleware performs response validation using dynamically inferred schemas:

### Schema Inference

```python
async def _infer_schema(self, response: Dict) -> Any:
    """Dynamically create a Pydantic model from a response payload."""
    fields = {}
    for key, value in response.items():
        python_type = type(value)
        fields[key] = (python_type, ...)
    return create_model("DynamicResponse", **fields)
```

### Validation

After receiving a response from the tool, the middleware:

1. Infers a schema from the response structure
2. Validates the response against the schema
3. If validation fails, logs a warning and triggers drift detection
4. Records the validation result in the trace

---

## Middleware Pipeline

The full middleware pipeline for a single routing call:

```
1. Check circuit breaker → if OPEN, reject immediately
2. Generate idempotency key → if duplicate, return cached result
3. Generate correlation ID
4. Execute with retry wrapper
   a. Send request to tool
   b. On transient failure → retry with backoff
   c. On permanent failure → record failure, break
5. Validate response schema
6. Record circuit breaker result (success/failure)
7. Cache result with idempotency key
8. Record trace
9. Return result
```

---

## TUI Trace Events

The middleware emits the following events to the TUI:

| Event | When | Message |
|---|---|---|
| Circuit trip | Circuit breaker opens | `⚡ Circuit breaker OPENED for <dest>` |
| Retry attempt | Transient failure detected | `🔄 Retrying <dest> (attempt 2/3)` |
| Idempotency hit | Duplicate request detected | `📋 Idempotent result returned for <key>` |
| Schema validation | Response doesn't match schema | `⚠️ Schema mismatch in response from <tool>` |
| Recovery success | Probe succeeds in half-open | `✅ Circuit breaker CLOSED for <dest>` |

---

## Bridge Router

The `bridge/router.py` module provides the unified routing entrypoint that the reliability middleware wraps:

```python
async def routeTo(target_protocol: str, payload: dict, config: dict) -> dict:
    """
    Unified routing entrypoint.
    The reliability middleware wraps this function.
    """
    ...
```

This function:
1. Determines the target connector based on `target_protocol`
2. Normalizes the payload through the semantic mapper
3. Dispatches to the appropriate connector's `execute()` method
4. Returns the result

---

## Configuration

The reliability middleware uses sensible defaults but can be tuned:

| Setting | Where | Default | Description |
|---|---|---|---|
| Circuit breaker threshold | `reliability/middleware.py` | 5 failures | Consecutive failures before opening |
| Cooldown period | `reliability/middleware.py` | 30 seconds | Time before half-open transition |
| Retry attempts | `reliability/middleware.py` | 3 | Maximum retry attempts |
| Backoff multiplier | `reliability/middleware.py` | 1 | Exponential backoff multiplier |
| Idempotency TTL | `reliability/middleware.py` | 300 seconds | How long idempotency keys are cached |

---

## What's Next

- **[Architecture](./17-architecture.md)** — System-level view of where reliability fits
- **[Observability & Tracing](./14-observability-tracing.md)** — Monitor reliability events
- **[Self-Healing Engine](./09-self-healing-engine.md)** — How schema validation feeds into healing
