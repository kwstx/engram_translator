import logging
import re
from typing import Optional, Any, Dict

import structlog

from app.core.config import settings

SENSITIVE_KEYS = {"token", "password", "key", "secret", "authorization", "cookie", "jwt", "auth"}

def mask_sensitive_data(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Masks values of sensitive keys in the log event."""
    for key in event_dict:
        if any(sk in key.lower() for sk in SENSITIVE_KEYS):
            val = event_dict[key]
            if isinstance(val, str) and len(val) > 8:
                event_dict[key] = f"{val[:4]}...{val[-4:]}"
            else:
                event_dict[key] = "********"
    return event_dict

def configure_logging(log_level: Optional[str] = None) -> None:
    """Configure structured JSON logging via structlog."""
    level = (log_level or settings.LOG_LEVEL).upper()

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    pre_chain = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=pre_chain,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    from app.core.tui_bridge import tui_logger_processor
    structlog.configure(
        processors=pre_chain
        + [
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            mask_sensitive_data,
            tui_logger_processor,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

