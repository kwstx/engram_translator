from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from sqlmodel import select

from app.core.config import settings
from app.db.models import MappingFailureLog, ProtocolMapping, ProtocolType
from app.semantic.ml_mapper import MappingPredictor


def extract_fields(payload: Dict[str, Any], max_fields: int) -> List[str]:
    fields: List[str] = []
    stack: List[tuple[str, Any]] = [("", payload)]

    while stack and len(fields) < max_fields:
        prefix, value = stack.pop()
        if isinstance(value, dict):
            for key, child in value.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                stack.append((path, child))
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                path = f"{prefix}[{idx}]"
                stack.append((path, child))
        else:
            if prefix:
                fields.append(prefix)
    return fields


def extract_payload_excerpt(payload: Dict[str, Any], max_keys: int) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {"value": payload}
    excerpt: Dict[str, Any] = {}
    for idx, (key, value) in enumerate(payload.items()):
        if idx >= max_keys:
            break
        excerpt[key] = value
    return excerpt


async def log_mapping_failure(
    session,
    *,
    source_protocol: str,
    target_protocol: str,
    source_field: str,
    payload_excerpt: Dict[str, Any],
    error_type: str,
) -> MappingFailureLog:
    entry = MappingFailureLog(
        source_protocol=source_protocol.upper(),
        target_protocol=target_protocol.upper(),
        source_field=source_field,
        payload_excerpt=payload_excerpt,
        error_type=error_type,
    )
    session.add(entry)
    return entry


async def apply_ml_suggestion(
    session,
    entry: MappingFailureLog,
) -> Optional[MappingFailureLog]:
    if not settings.ML_ENABLED:
        return None

    predictor = MappingPredictor.load_or_none(settings.ML_MODEL_PATH)
    if not predictor:
        return None

    prediction = predictor.predict(
        entry.source_protocol, entry.target_protocol, entry.source_field
    )
    if not prediction:
        return None

    entry.model_suggestion = prediction.suggestion
    entry.model_confidence = prediction.confidence

    if prediction.confidence < settings.ML_AUTO_APPLY_THRESHOLD:
        return entry

    try:
        proto_enum = ProtocolType[entry.source_protocol.upper()]
    except KeyError:
        return entry

    result = await session.execute(
        select(ProtocolMapping).where(
            (ProtocolMapping.source_protocol == proto_enum)
            & (ProtocolMapping.target_protocol == entry.target_protocol.upper())
        )
    )
    mapping = result.scalars().first()
    if not mapping:
        mapping = ProtocolMapping(
            source_protocol=proto_enum,
            target_protocol=entry.target_protocol.upper(),
            mapping_rules={},
            semantic_equivalents={},
        )
        session.add(mapping)

    semantic = mapping.semantic_equivalents or {}
    semantic[entry.source_field] = prediction.suggestion
    mapping.semantic_equivalents = semantic
    entry.applied = True
    return entry
