import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.mapping_failures import extract_fields, extract_payload_excerpt, log_mapping_failure, apply_ml_suggestion
from app.db.models import MappingFailureLog, ProtocolMapping, ProtocolType

def test_extract_fields():
    payload = {"user": {"name": "A", "meta": [1, 2]}, "task": "T"}
    fields = extract_fields(payload, max_fields=10)
    assert "task" in fields
    assert "user.name" in fields
    assert "user.meta[0]" in fields
    assert "user.meta[1]" in fields

def test_extract_payload_excerpt():
    payload = {"a": 1, "b": 2, "c": 3}
    excerpt = extract_payload_excerpt(payload, max_keys=2)
    assert len(excerpt) == 2
    assert "a" in excerpt
    assert "b" in excerpt
    assert "c" not in excerpt

@pytest.mark.asyncio
async def test_log_mapping_failure():
    session = MagicMock()
    entry = await log_mapping_failure(
        session,
        source_protocol="A2A",
        target_protocol="MCP",
        source_field="f1",
        payload_excerpt={},
        error_type="missing"
    )
    assert entry.source_protocol == "A2A"
    assert entry.source_field == "f1"
    session.add.assert_called_with(entry)

@pytest.mark.asyncio
@patch("app.services.mapping_failures.MappingPredictor")
@patch("app.services.mapping_failures.settings")
async def test_apply_ml_suggestion_low_confidence(mock_settings, mock_predictor_cls):
    mock_settings.ML_ENABLED = True
    mock_settings.ML_AUTO_APPLY_THRESHOLD = 0.9
    
    mock_predictor = MagicMock()
    mock_predictor.predict.return_value = MagicMock(suggestion="s1", confidence=0.5)
    mock_predictor_cls.load_or_none.return_value = mock_predictor
    
    session = AsyncMock()
    entry = MappingFailureLog(source_protocol="A2A", target_protocol="MCP", source_field="f1")
    
    result = await apply_ml_suggestion(session, entry)
    
    assert result.model_suggestion == "s1"
    assert result.model_confidence == 0.5
    assert result.applied is False

@pytest.mark.asyncio
@patch("app.services.mapping_failures.MappingPredictor")
@patch("app.services.mapping_failures.settings")
async def test_apply_ml_suggestion_auto_apply(mock_settings, mock_predictor_cls):
    mock_settings.ML_ENABLED = True
    mock_settings.ML_AUTO_APPLY_THRESHOLD = 0.8
    
    mock_predictor = MagicMock()
    mock_predictor.predict.return_value = MagicMock(suggestion="target_f", confidence=0.9)
    mock_predictor_cls.load_or_none.return_value = mock_predictor
    
    session = AsyncMock()
    # Mock existing mapping query
    mock_mapping = ProtocolMapping(source_protocol=ProtocolType.A2A, target_protocol="MCP", semantic_equivalents={})
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_mapping
    session.execute.return_value = mock_result
    
    entry = MappingFailureLog(source_protocol="A2A", target_protocol="MCP", source_field="source_f")
    
    result = await apply_ml_suggestion(session, entry)
    
    assert result.applied is True
    assert mock_mapping.semantic_equivalents["source_f"] == "target_f"
    assert session.execute.called
