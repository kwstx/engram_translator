"""
Unit tests for TranslatorEngine.

Run with:
    python -m pytest app/core/test_translator.py -v
"""
from datetime import datetime, date
import pytest

from app.core.translator import TranslatorEngine
from app.core.exceptions import ProtocolMismatchError, TranslationError


class TestTranslatorEngine:
    def test_supported_pairs(self):
        engine = TranslatorEngine()
        assert ("A2A", "MCP") in engine.supported_pairs

    def test_translate_a2a_to_mcp_payload_to_data_bundle(self):
        engine = TranslatorEngine()
        msg = {
            "id": "msg-1",
            "payload": {"task": "compute"},
        }

        result = engine.translate(msg, "A2A", "MCP")
        assert "data_bundle" in result
        assert "payload" not in result
        assert result["data_bundle"]["task"] == "compute"

    def test_translate_a2a_to_mcp_serializes_dates(self):
        engine = TranslatorEngine()
        msg = {
            "payload": {
                "due": date(2026, 3, 15),
                "updated": datetime(2026, 3, 15, 12, 0, 0),
            }
        }

        result = engine.translate(msg, "A2A", "MCP")
        bundle = result["data_bundle"]
        assert bundle["due"] == "2026-03-15"
        assert bundle["updated"] == "2026-03-15T12:00:00"

    def test_translate_a2a_to_mcp_data_task_to_coord(self):
        engine = TranslatorEngine()
        msg = {"protocol": "A2A", "data": {"task": "compute"}}

        result = engine.translate(msg, "A2A", "MCP")
        assert result == {"coord": "compute"}

    def test_unsupported_pair_raises(self):
        engine = TranslatorEngine()
        with pytest.raises(ProtocolMismatchError):
            engine.translate({"payload": {}}, "MCP", "A2A")

    def test_translation_error_is_wrapped(self):
        engine = TranslatorEngine()

        def boom(_):
            raise ValueError("kaboom")

        engine._mappers[("A2A", "MCP")] = boom

        with pytest.raises(TranslationError, match="kaboom"):
            engine.translate({"payload": {}}, "A2A", "MCP")

    def test_version_delta_applies_rename(self):
        engine = TranslatorEngine()
        engine.register_delta_mapping(
            "A2A",
            "1",
            "2",
            {"rename": {"old_field": "new_field"}},
        )

        msg = {
            "protocol_version": "v1",
            "old_field": "legacy",
            "payload": {"task": "compute"},
        }

        result = engine.translate(msg, "A2A", "MCP")
        assert result["new_field"] == "legacy"
        assert "old_field" not in result
        assert result["protocol_version"] == "2"

    def test_version_mismatch_without_delta_raises(self):
        engine = TranslatorEngine()
        msg = {"protocol_version": "1", "payload": {"task": "compute"}}

        with pytest.raises(TranslationError, match="delta mappings"):
            engine.translate(msg, "A2A", "MCP")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
