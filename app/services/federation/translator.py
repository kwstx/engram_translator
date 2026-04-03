from typing import Any, Dict, List, Optional
import structlog
from app.semantic.mapper import SemanticMapper
from app.core.config import settings

logger = structlog.get_logger(__name__)

class FederationTranslator:
    """
    Translation modules for cross-protocol federation.
    Converts between MCP, CLI, and canonical ontology representations.
    """

    def __init__(self, semantic_mapper: Optional[SemanticMapper] = None):
        self.mapper = semantic_mapper or SemanticMapper(settings.DEFAULT_ONTOLOGY_PATH)

    def mcp_to_cli(self, mcp_tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates an MCP (Model Context Protocol) tool call to a CLI execution.
        """
        logger.info("Translating MCP to CLI", tool=mcp_tool_call.get("name"))
        
        # 1. Map name to canonical concept
        canonical_name = self.mapper.resolve_to_ontology_concept(mcp_tool_call.get("name"), "MCP")
        
        # 2. Map back to CLI (if target protocol not specified, we assume we want CLI)
        cli_name = self.mapper.resolve_from_ontology_concept(canonical_name, "CLI")
        
        # 3. Handle arguments via DataSiloResolver (flattens and renames)
        # Assuming schemas are available via some registry or provided in context
        # For simplicity, we just use resolve_equivalent for each argument key
        cli_args = {}
        for k, v in mcp_tool_call.get("arguments", {}).items():
            arg_canonical = self.mapper.resolve_to_ontology_concept(k, "MCP")
            arg_cli = self.mapper.resolve_from_ontology_concept(arg_canonical, "CLI")
            cli_args[arg_cli] = v
            
        return {
            "command": cli_name,
            "args": cli_args,
            "canonical_concept": canonical_name
        }

    def cli_to_mcp(self, cli_execution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a CLI execution back to an MCP tool call response or intent.
        """
        logger.info("Translating CLI to MCP", command=cli_execution.get("command"))
        
        canonical_name = self.mapper.resolve_to_ontology_concept(cli_execution.get("command"), "CLI")
        mcp_name = self.mapper.resolve_from_ontology_concept(canonical_name, "MCP")
        
        mcp_args = {}
        for k, v in cli_execution.get("args", {}).items():
            arg_canonical = self.mapper.resolve_to_ontology_concept(k, "CLI")
            arg_mcp = self.mapper.resolve_from_ontology_concept(arg_canonical, "MCP")
            mcp_args[arg_mcp] = v
            
        return {
            "name": mcp_name,
            "arguments": mcp_args,
            "canonical_concept": canonical_name
        }

    def to_ontology(self, payload: Dict[str, Any], source_protocol: str) -> Dict[str, Any]:
        """
        Maps a protocol-specific payload to its canonical intermediate representation.
        """
        logger.info(f"Mapping {source_protocol} to canonical ontology")
        
        canonical_payload = {}
        for k, v in payload.items():
            canonical_key = self.mapper.resolve_to_ontology_concept(k, source_protocol)
            canonical_payload[canonical_key] = v
            
        return canonical_payload

    def from_ontology(self, canonical_payload: Dict[str, Any], target_protocol: str) -> Dict[str, Any]:
        """
        Maps from the canonical intermediate representation to a target protocol.
        """
        logger.info(f"Mapping canonical ontology to {target_protocol}")
        
        target_payload = {}
        for k, v in canonical_payload.items():
            target_key = self.mapper.resolve_from_ontology_concept(k, target_protocol)
            target_payload[target_key] = v
            
        return target_payload
