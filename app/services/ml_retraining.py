from __future__ import annotations

import structlog
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import ProtocolMapping
from app.semantic.ml_mapper import MappingPredictor

logger = structlog.get_logger(__name__)

async def retrain_mapping_model(session: AsyncSession) -> bool:
    """
    Retrains the mapping model using all currently established ProtocolMapping entries.
    Saves the new model to settings.ML_MODEL_PATH.
    """
    if not settings.ML_ENABLED:
        logger.info("ML retraining skipped: ML is disabled.")
        return False

    logger.info("Starting ML model retraining...")
    
    result = await session.execute(select(ProtocolMapping))
    mappings = result.scalars().all()
    
    predictor = MappingPredictor.train_from_mappings(mappings)
    
    if predictor:
        predictor.save(settings.ML_MODEL_PATH)
        logger.info("ML model retraining completed successfully.")
        return True
    else:
        logger.warning("ML model retraining failed: Not enough training data or labels.")
        return False
