import asyncio

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.session import engine
from app.db.models import ProtocolMapping
from app.semantic.ml_mapper import MappingPredictor


async def _train() -> int:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(ProtocolMapping))
        mappings = result.scalars().all()

    predictor = MappingPredictor.train_from_mappings(mappings)
    if predictor is None:
        print("Not enough data to train a model.")
        return 1

    predictor.save(settings.ML_MODEL_PATH)
    print(f"Model saved to {settings.ML_MODEL_PATH}")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_train()))


if __name__ == "__main__":
    main()
