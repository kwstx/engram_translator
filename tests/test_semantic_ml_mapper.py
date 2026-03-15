import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from app.semantic.ml_mapper import MappingPredictor, MappingPrediction
from app.db.models import ProtocolMapping, ProtocolType

def test_build_text():
    text = MappingPredictor._build_text("A2A", "MCP", "user_name")
    assert text == "A2A::MCP::user_name"

def test_train_from_mappings_not_enough_samples():
    mappings = [ProtocolMapping(source_protocol="A2A", target_protocol="MCP", semantic_equivalents={"a": "b"})]
    # Default settings.ML_MIN_TRAIN_SAMPLES is 20
    predictor = MappingPredictor.train_from_mappings(mappings)
    assert predictor is None

def test_train_and_predict_integration():
    # Setup some training data
    mappings = []
    semantic = {f"field_{i}": f"target_{i}" for i in range(25)}
    # Need diversity in labels for LogisticRegression
    for i in range(12):
        semantic[f"field_{i}"] = "LabelA"
    for i in range(12, 25):
        semantic[f"field_{i}"] = "LabelB"
        
    mappings.append(ProtocolMapping(
        source_protocol=ProtocolType.A2A,
        target_protocol="MCP",
        semantic_equivalents=semantic
    ))
    
    predictor = MappingPredictor.train_from_mappings(mappings)
    assert predictor is not None
    
    # Predict
    prediction = predictor.predict("A2A", "MCP", "field_1")
    assert isinstance(prediction, MappingPrediction)
    assert prediction.suggestion in ["LabelA", "LabelB"]
    assert 0 <= prediction.confidence <= 1.0

def test_save_load():
    predictor = MagicMock(spec=MappingPredictor)
    predictor._pipeline = MagicMock()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "model.joblib")
        # Real save/load using joblib
        from joblib import dump, load
        dump("mock_pipeline", model_path)
        
        loaded = MappingPredictor.load_or_none(model_path)
        assert loaded is not None
        assert loaded._pipeline == "mock_pipeline"

def test_load_or_none_missing():
    assert MappingPredictor.load_or_none("non_existent_file") is None
