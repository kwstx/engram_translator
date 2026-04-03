from __future__ import annotations
import asyncio
import structlog
from app.celery_app import celery_app
from app.db.session import get_session
from app.services.evolution import ToolEvolutionService
from app.db.views import create_evolution_feature_views

logger = structlog.get_logger(__name__)

@celery_app.task(name="app.tasks.evolution_tasks.run_evolution_loop_task")
def run_evolution_loop_task():
    """
    Background ML Pipeline for Tool Evolution.
    Executed via Celery Beat or manual trigger.
    """
    # Use sync wrapper for async DB session
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # New thread if needed, or task-based runner
        from threading import Thread
        thread = Thread(target=lambda: asyncio.run(_run_evolution_sync()))
        thread.start()
    else:
        asyncio.run(_run_evolution_sync())

async def _run_evolution_sync():
    """
    Runs the evolution logic using the Service.
    """
    logger.info("Starting background evolution pipeline...")
    
    # 1. Warm up Views (Feature Store aggregation)
    await create_evolution_feature_views()
    
    # 2. Run Evolution Loop
    from app.db.session import SessionLocal
    async with SessionLocal() as session:
        service = ToolEvolutionService(session)
        await service.run_evolution_loop()
    
    logger.info("Evolution pipeline completed successfully.")
