from collections import deque
from threading import Lock
import time

from prometheus_client import Counter, Gauge, Histogram

# Translation Metrics
TRANSLATIONS_TOTAL = Counter(
    "translations_total",
    "Total number of translations completed",
    ["channel", "source_protocol", "target_protocol"],
)

TRANSLATION_ERRORS_TOTAL = Counter(
    "translation_errors_total",
    "Total number of translation errors",
    ["channel", "source_protocol", "target_protocol"],
)

TRANSLATIONS_PER_SECOND = Gauge(
    "translations_per_second",
    "Rolling translations per second over the last 60 seconds",
    ["channel"],
)

TRANSLATION_ERROR_RATE = Gauge(
    "translation_error_rate",
    "Rolling translation error rate over the last 60 seconds (0-1)",
    ["channel"],
)

# Task Metrics
TASKS_STARTED_TOTAL = Counter(
    "tasks_started_total",
    "Total number of tasks started",
    ["task_type", "user_id"],
)

TASKS_COMPLETED_TOTAL = Counter(
    "tasks_completed_total",
    "Total number of tasks completed",
    ["task_type", "user_id", "status"],
)

TASK_LATENCY_SECONDS = Histogram(
    "task_latency_seconds",
    "Task execution latency in seconds",
    ["task_type", "user_id"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float("inf")),
)

# Connector Metrics
CONNECTOR_CALLS_TOTAL = Counter(
    "connector_calls_total",
    "Total number of connector calls",
    ["connector", "user_id", "status"],
)

CONNECTOR_LATENCY_SECONDS = Histogram(
    "connector_latency_seconds",
    "Connector call latency in seconds",
    ["connector", "user_id"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, float("inf")),
)

_WINDOW_SECONDS = 60
_success_events_by_channel: dict[str, deque] = {}
_error_events_by_channel: dict[str, deque] = {}
_lock = Lock()


def _update_rates(channel: str, now: float) -> None:
    success_events = _success_events_by_channel.setdefault(channel, deque())
    error_events = _error_events_by_channel.setdefault(channel, deque())
    cutoff = now - _WINDOW_SECONDS
    while success_events and success_events[0] < cutoff:
        success_events.popleft()
    while error_events and error_events[0] < cutoff:
        error_events.popleft()

    total = len(success_events) + len(error_events)
    TRANSLATIONS_PER_SECOND.labels(channel=channel).set(
        len(success_events) / _WINDOW_SECONDS
    )
    TRANSLATION_ERROR_RATE.labels(channel=channel).set(
        (len(error_events) / total) if total else 0.0
    )


def record_translation_success(
    channel: str,
    source_protocol: str = "unknown",
    target_protocol: str = "unknown",
) -> None:
    TRANSLATIONS_TOTAL.labels(
        channel=channel,
        source_protocol=source_protocol,
        target_protocol=target_protocol,
    ).inc()
    now = time.time()
    with _lock:
        _success_events_by_channel.setdefault(channel, deque()).append(now)
        _update_rates(channel, now)


def record_translation_error(
    channel: str,
    source_protocol: str = "unknown",
    target_protocol: str = "unknown",
) -> None:
    TRANSLATION_ERRORS_TOTAL.labels(
        channel=channel,
        source_protocol=source_protocol,
        target_protocol=target_protocol,
    ).inc()
    now = time.time()
    with _lock:
        _error_events_by_channel.setdefault(channel, deque()).append(now)
        _update_rates(channel, now)


def record_task_start(task_type: str, user_id: str) -> None:
    TASKS_STARTED_TOTAL.labels(task_type=task_type, user_id=user_id).inc()


def record_task_completion(
    task_type: str, user_id: str, status: str, duration: float
) -> None:
    TASKS_COMPLETED_TOTAL.labels(
        task_type=task_type, user_id=user_id, status=status
    ).inc()
    TASK_LATENCY_SECONDS.labels(task_type=task_type, user_id=user_id).observe(duration)


def record_connector_call(
    connector: str, user_id: str, status: str, duration: float
) -> None:
    CONNECTOR_CALLS_TOTAL.labels(
        connector=connector, user_id=user_id, status=status
    ).inc()
    CONNECTOR_LATENCY_SECONDS.labels(connector=connector, user_id=user_id).observe(
        duration
    )
