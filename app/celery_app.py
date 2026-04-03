from __future__ import annotations
import os
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Celery instance
celery_app = Celery(
    "engram_evolution",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.tasks.evolution_tasks"]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    "run-tool-evolution-pipeline-daily": {
        "task": "app.tasks.evolution_tasks.run_evolution_loop_task",
        "schedule": crontab(hour=2, minute=0), # Run daily at 2:00 AM
    },
}
