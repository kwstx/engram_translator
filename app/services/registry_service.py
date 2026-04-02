import subprocess
import json
import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import structlog
from sqlmodel import Session, select
from prance import ResolvingParser
from openapi_spec_validator import validate_spec
import strawberry
from graphql import parse, build_ast_schema

from app.db.models import ToolRegistry, ToolExecutionMetadata, ExecutionType, AgentRegistry
from app.core.exceptions import ValidationError
from app.services.llm import LLMService

logger = structlog.get_logger(__name__)

class RegistryService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMService()

    async def ingest_openapi(self, url_or_path: str, agent_id: uuid.UUID) -> ToolRegistry:
        """Ingest tools from an OpenAPI spec."""
        try:
            parser = ResolvingParser(url_or_path)
            spec = parser.specification
            
            tool_name = spec.get("info", {}).get("title", "OpenAPI Tool")
            description = spec.get("info", {}).get("description", "No description provided")
            
            # Map paths to actions
            actions = []
            for path, methods in spec.get("paths", {}).items():
                for method, details in methods.items():
                    action = {
                        "name": f"{method.upper()} {path}",
                        "description": details.get("summary") or details.get("description", ""),
                        "parameters": details.get("parameters", []),
                        "request_body": details.get("requestBody", {}),
                    }
                    actions.append(action)

            tool = ToolRegistry(
                agent_id=agent_id,
                name=tool_name,
                description=description,
                actions=actions
            )
            self.db.add(tool)
            self.db.flush()

            execution_metadata = ToolExecutionMetadata(
                tool_id=tool.id,
                execution_type=ExecutionType.HTTP,
                metadata={"openapi_spec": spec, "source_url": url_or_path}
            )
            self.db.add(execution_metadata)
            self.db.commit()
            self.db.refresh(tool)
            return tool
        except Exception as e:
            logger.error("Failed to ingest OpenAPI", error=str(e))
            raise ValidationError(f"OpenAPI ingestion failed: {str(e)}")

    async def ingest_graphql(self, url: str, agent_id: uuid.UUID, auth_details: Optional[Dict[str, Any]] = None) -> ToolRegistry:
        """Ingest tools from a GraphQL service via introspection."""
        # For simplicity, we create a generic GraphQL tool entry.
        # In a real implementation, we would perform an introspection query and populate actions.
        
        tool = ToolRegistry(
            agent_id=agent_id,
            name=f"GraphQL Service ({url})",
            description="Auto-onboarded GraphQL API",
            actions=[{"name": "query", "description": "Generic GraphQL query execution"}]
        )
        self.db.add(tool)
        self.db.flush()

        execution_metadata = ToolExecutionMetadata(
            tool_id=tool.id,
            execution_type=ExecutionType.HTTP,
            metadata={"graphql_url": url},
            auth_config=auth_details or {}
        )
        self.db.add(execution_metadata)
        self.db.commit()
        return tool

    async def ingest_url_with_auth(self, url: str, agent_id: uuid.UUID, auth: Dict[str, Any]) -> ToolRegistry:
        """Onboard a raw URL with specified auth details."""
        tool = ToolRegistry(
            agent_id=agent_id,
            name=f"HTTP Endpoint ({url})",
            description="Manually onboarded URL",
            actions=[{"name": "call", "description": "Call the specific URL"}]
        )
        self.db.add(tool)
        self.db.flush()

        execution_metadata = ToolExecutionMetadata(
            tool_id=tool.id,
            execution_type=ExecutionType.HTTP,
            metadata={"endpoint_url": url},
            auth_config=auth
        )
        self.db.add(execution_metadata)
        self.db.commit()
        return tool

    async def ingest_cli_help(self, command: str, agent_id: uuid.UUID) -> ToolRegistry:
        """Parse --help output of a CLI tool and create a thin wrapper."""
        try:
            result = subprocess.run([command, "--help"], capture_output=True, text=True, check=True)
            help_text = result.stdout
            
            # Use regex/LLM to extract argument structure
            args = re.findall(r"(--\w+)\s+(\w+)?", help_text)
            actions = [{"name": command, "description": help_text[:500], "args": [a[0] for a in args]}]

            tool = ToolRegistry(
                agent_id=agent_id,
                name=command,
                description=f"CLI wrapper for {command}",
                actions=actions
            )
            self.db.add(tool)
            self.db.flush()

            # Python template for the thin wrapper
            cli_wrapper_script = (
                "#!/usr/bin/env python\n"
                "import os, subprocess, sys\n"
                "def run():\n"
                "    # Credentials injected via env vars from EAT\n"
                f"    base_cmd = '{command}'\n"
                "    subprocess.run([base_cmd] + sys.argv[1:])\n"
                "if __name__ == '__main__':\n"
                "    run()"
            )

            execution_metadata = ToolExecutionMetadata(
                tool_id=tool.id,
                execution_type=ExecutionType.CLI,
                cli_wrapper=cli_wrapper_script,
                metadata={"cli_command": command, "help_output": help_text}
            )
            self.db.add(execution_metadata)
            self.db.commit()
            return tool
        except Exception as e:
            logger.error("CLI help ingestion failed", command=command, error=str(e))
            raise ValidationError(f"CLI ingestion failed: {str(e)}")

    async def extract_from_docs(self, docs_text: str, agent_id: uuid.UUID) -> ToolRegistry:
        """Use LLM-assisted extraction (Phi-3/LLMService) to register a tool from partial docs."""
        extracted = await self.llm.extract_tool_schema(docs_text)
        
        tool = ToolRegistry(
            agent_id=agent_id,
            name=extracted["name"],
            description=extracted["description"],
            actions=extracted["actions"]
        )
        self.db.add(tool)
        self.db.flush()

        execution_metadata = ToolExecutionMetadata(
            tool_id=tool.id,
            execution_type=ExecutionType.MCP,
            metadata={"extracted_from": "docs", "raw_content_preview": docs_text[:200]}
        )
        self.db.add(execution_metadata)
        self.db.commit()
        return tool
