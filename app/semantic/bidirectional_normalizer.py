from __future__ import annotations

from typing import Any, Dict, Optional
import structlog
from datetime import datetime, timezone

from app.semantic.mapper import SemanticMapper
from app.reconciliation.engine import reconciliation_engine

logger = structlog.get_logger(__name__)


class BidirectionalNormalizer:
    """
    Normalizes payloads to a canonical ontology representation and back out to protocol/CLI forms.
    """

    def __init__(self, ontology_path: str = "app/semantic/protocols.owl") -> None:
        self.mapper = SemanticMapper(ontology_path=ontology_path)

    def normalize_to_ontology(
        self,
        payload: Dict[str, Any],
        source_protocol: str,
        *,
        field_rules: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        flattened = self.mapper._flatten_dict(payload)
        ontology_payload: Dict[str, Any] = {}
        field_map: Dict[str, str] = {}

        for field, value in flattened.items():
            leaf = field.split(".")[-1]
            concept = None
            if field_rules and field in field_rules:
                concept = field_rules[field]
            if not concept:
                concept = self.mapper.resolve_to_ontology_concept(leaf, source_protocol)
            if not concept or concept.startswith("Error"):
                concept = leaf

            if concept == leaf:
                try:
                    similarities = reconciliation_engine.compute_similarity(leaf)
                    if similarities:
                        best_match, score = similarities[0]
                        if score >= reconciliation_engine.similarity_threshold:
                            concept = best_match
                except Exception as exc:
                    logger.warning("Ontology similarity lookup failed", field=leaf, error=str(exc))

            ontology_payload[concept] = value
            field_map[field] = concept

        return {
            "ontology": ontology_payload,
            "field_map": field_map,
            "source_protocol": source_protocol,
            "normalized_at": datetime.now(timezone.utc).isoformat(),
        }

    def normalize_from_ontology(
        self,
        ontology_payload: Dict[str, Any],
        target_protocol: str,
        *,
        field_rules: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        output: Dict[str, Any] = {}
        for concept, value in ontology_payload.items():
            target_field = concept
            if field_rules and concept in field_rules:
                target_field = field_rules[concept]
            else:
                target_field = self.mapper.resolve_from_ontology_concept(concept, target_protocol)
            output[target_field] = value
        return output

    def ontology_to_cli(
        self,
        ontology_payload: Dict[str, Any],
        cli_command: str,
        *,
        cli_args: Optional[list[str]] = None,
        arg_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        cli_args = cli_args or []
        arg_map = arg_map or {}
        args: list[str] = []

        available = {arg.lstrip("-") for arg in cli_args}
        for concept, value in ontology_payload.items():
            target_arg = arg_map.get(concept) or concept
            if target_arg in available or f"--{target_arg}" in cli_args:
                args.append(f"--{target_arg}={value}")
            else:
                # Best-effort: include as generic argument
                args.append(str(value))

        return {"command": cli_command, "args": args}
