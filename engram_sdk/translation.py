from __future__ import annotations

from typing import Any, Dict, List, Optional

from .communication import EngramTransport
from .types import MappingSuggestion, TranslationResponse


class TranslationClient:
    def __init__(self, transport: EngramTransport) -> None:
        self._transport = transport

    def translate(
        self,
        payload: Dict[str, Any],
        *,
        source_protocol: Optional[str] = None,
        target_protocol: Optional[str] = None,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
        beta: bool = False,
    ) -> TranslationResponse:
        """
        Translates a protocol-specific payload using the Engram Translation Layer.
        
        If source_agent and target_agent are provided, the system retrieves their 
        preferred protocols from the registry automatically.
        """
        if source_agent and target_agent:
            request_payload = {
                "source_agent": source_agent,
                "target_agent": target_agent,
                "payload": payload,
            }
            endpoint = "/translate"
        elif source_protocol and target_protocol:
            request_payload = {
                "source_protocol": source_protocol,
                "target_protocol": target_protocol,
                "payload": payload,
            }
            endpoint = "/beta/translate" if beta else "/translate"
        else:
            raise ValueError(
                "Either (source_agent, target_agent) or (source_protocol, target_protocol) must be provided."
            )

        response = self._transport.request_json(
            "POST",
            endpoint,
            json_body=request_payload,
        )

        suggestions = []
        for s in response.get("mapping_suggestions", []):
            suggestions.append(
                MappingSuggestion(
                    source_field=s.get("source_field"),
                    suggestion=s.get("suggestion"),
                    confidence=s.get("confidence"),
                    applied=s.get("applied", False),
                )
            )

        return TranslationResponse(
            status=str(response.get("status")),
            message=str(response.get("message")),
            payload=response.get("payload") or {},
            mapping_suggestions=suggestions,
        )

    def playground_translate(
        self,
        payload: Dict[str, Any],
        source_protocol: str,
        target_protocol: str,
    ) -> TranslationResponse:
        """
        Sandbox translation for rapid prototyping; doesn't require authentication.
        """
        request_payload = {
            "source_protocol": source_protocol,
            "target_protocol": target_protocol,
            "payload": payload,
        }
        
        response = self._transport.request_json(
            "POST",
            "/beta/playground/translate",
            json_body=request_payload,
            auth=None,
        )

        return TranslationResponse(
            status=str(response.get("status")),
            message=str(response.get("message")),
            payload=response.get("payload") or {},
        )
