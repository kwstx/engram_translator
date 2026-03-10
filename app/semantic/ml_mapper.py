from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional
import os

import structlog
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.core.config import settings
from app.db.models import ProtocolMapping

logger = structlog.get_logger(__name__)


@dataclass
class MappingPrediction:
    suggestion: str
    confidence: float


class MappingPredictor:
    def __init__(self, pipeline: Pipeline):
        self._pipeline = pipeline

    @staticmethod
    def _build_text(source_protocol: str, target_protocol: str, source_field: str) -> str:
        return f"{source_protocol.upper()}::{target_protocol.upper()}::{source_field}"

    def predict(
        self, source_protocol: str, target_protocol: str, source_field: str
    ) -> Optional[MappingPrediction]:
        if not self._pipeline:
            return None
        text = self._build_text(source_protocol, target_protocol, source_field)
        try:
            probabilities = self._pipeline.predict_proba([text])[0]
        except Exception as exc:
            logger.warning("ML prediction failed", error=str(exc))
            return None
        classes = self._pipeline.classes_
        best_index = int(probabilities.argmax())
        return MappingPrediction(
            suggestion=str(classes[best_index]),
            confidence=float(probabilities[best_index]),
        )

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        dump(self._pipeline, path)
        logger.info("ML model saved", path=path)

    @classmethod
    def load(cls, path: str) -> "MappingPredictor":
        pipeline = load(path)
        return cls(pipeline)

    @classmethod
    def load_or_none(cls, path: str) -> Optional["MappingPredictor"]:
        if not os.path.exists(path):
            return None
        try:
            return cls.load(path)
        except Exception as exc:
            logger.warning("Failed to load ML model", error=str(exc))
            return None

    @classmethod
    def train_from_mappings(
        cls, mappings: Iterable[ProtocolMapping]
    ) -> Optional["MappingPredictor"]:
        rows: list[tuple[str, str, str, str]] = []
        for mapping in mappings:
            source_protocol = str(mapping.source_protocol)
            target_protocol = str(mapping.target_protocol)
            semantic = mapping.semantic_equivalents or {}
            for source_field, target_field in semantic.items():
                if not source_field or not target_field:
                    continue
                rows.append(
                    (source_protocol, target_protocol, str(source_field), str(target_field))
                )

        if len(rows) < settings.ML_MIN_TRAIN_SAMPLES:
            logger.info(
                "Not enough training samples",
                sample_count=len(rows),
                min_required=settings.ML_MIN_TRAIN_SAMPLES,
            )
            return None

        labels = {row[3] for row in rows}
        if len(labels) < 2:
            logger.info("Not enough label diversity for training")
            return None

        texts = [cls._build_text(r[0], r[1], r[2]) for r in rows]
        targets = [r[3] for r in rows]

        pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5))),
                ("clf", LogisticRegression(max_iter=1000)),
            ]
        )
        pipeline.fit(texts, targets)
        logger.info("ML model trained", samples=len(rows), labels=len(labels))
        return cls(pipeline)
