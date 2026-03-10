from collections import deque
from threading import Lock
import time

from prometheus_client import Counter, Gauge

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
