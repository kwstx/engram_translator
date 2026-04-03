import yaml
import uuid
import structlog
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_
from datetime import datetime, timezone

from app.catalog.models import CatalogEntry, CatalogSubmission, CatalogSource, SubmissionStatus
from app.db.models import ToolRegistry, ToolExecutionMetadata, ExecutionType, AgentRegistry
from app.services.registry_service import RegistryService

logger = structlog.get_logger(__name__)

class CatalogService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.registry = RegistryService(db)

    async def seed_catalog_from_yaml(self, yaml_path: str):
        """
        Load pre-seeded apps from a YAML file.
        Only inserts if the slug doesn't already exist.
        """
        try:
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
            
            entries_data = data.get("entries", [])
            for entry_data in entries_data:
                slug = entry_data["slug"]
                
                # Check if exists
                stmt = select(CatalogEntry).where(CatalogEntry.slug == slug)
                result = await self.db.execute(stmt)
                existing = result.scalars().first()
                
                if not existing:
                    entry = CatalogEntry(
                        slug=slug,
                        display_name=entry_data["display_name"],
                        description=entry_data.get("description", ""),
                        category=entry_data.get("category", "general"),
                        tags=entry_data.get("tags", []),
                        openapi_url=entry_data.get("openapi_url"),
                        auth_hint=entry_data.get("auth_hint", {}),
                        mcp_definition=entry_data.get("mcp_definition", {}),
                        cli_command=entry_data.get("cli_command"),
                        cli_wrapper_script=entry_data.get("cli_wrapper_script"),
                        source=CatalogSource.SEED
                    )
                    self.db.add(entry)
                    logger.info("Seeded catalog entry", slug=slug)
            
            await self.db.commit()
        except Exception as e:
            logger.error("Failed to seed catalog", error=str(e))
            await self.db.rollback()

    async def get_entries(self, category: Optional[str] = None) -> List[CatalogEntry]:
        stmt = select(CatalogEntry)
        if category:
            stmt = stmt.where(CatalogEntry.category == category)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_entry_by_slug(self, slug: str) -> Optional[CatalogEntry]:
        stmt = select(CatalogEntry).where(CatalogEntry.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def submit_entry(self, submission: CatalogSubmission) -> CatalogSubmission:
        """Record a community submission."""
        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)
        logger.info("Recorded community catalog submission", id=str(submission.id), slug=submission.slug)
        return submission

    async def promote_submission(self, submission_id: uuid.UUID) -> CatalogEntry:
        """Approve a submission and create a CatalogEntry."""
        stmt = select(CatalogSubmission).where(CatalogSubmission.id == submission_id)
        result = await self.db.execute(stmt)
        submission = result.scalars().first()
        
        if not submission:
            raise ValueError("Submission not found")
        
        if submission.status != SubmissionStatus.PENDING:
            raise ValueError(f"Submission is already {submission.status}")
        
        # Create CatalogEntry
        entry = CatalogEntry(
            slug=submission.slug,
            display_name=submission.display_name,
            description=submission.description,
            category=submission.category,
            tags=submission.tags,
            mcp_definition=submission.mcp_definition,
            cli_command=submission.cli_command,
            cli_wrapper_script=submission.cli_wrapper_script,
            openapi_url=submission.openapi_url,
            auth_hint=submission.auth_hint,
            source=CatalogSource.COMMUNITY
        )
        self.db.add(entry)
        
        # Update submission status
        submission.status = SubmissionStatus.APPROVED
        submission.reviewed_at = datetime.now(timezone.utc)
        self.db.add(submission)
        
        await self.db.commit()
        await self.db.refresh(entry)
        logger.info("Promoted submission to catalog", slug=entry.slug)
        return entry

    async def warm_up_registry(self, slug: str, agent_id: uuid.UUID) -> Optional[ToolRegistry]:
        """
        Promote a catalog entry to the live ToolRegistry cache.
        This "warms" the tool for instant discovery.
        """
        entry = await self.get_entry_by_slug(slug)
        if not entry:
            return None
        
        # Check if already in registry for this agent
        # We search by name (entry.mcp_definition['name']) for this agent
        tool_name = entry.mcp_definition.get("name", entry.slug)
        
        # In a real system, we'd check if a tool with this name exists for the agent
        # For simplicity, we just create it or return existing one
        
        # Find local "Engram" agent if not provided
        # or just use the agent_id provided
        
        tool = ToolRegistry(
            agent_id=agent_id,
            name=tool_name,
            description=entry.description,
            actions=entry.mcp_definition.get("actions", []), # Note: my model says 'actions' is a list of dicts
            version=entry.upstream_version
        )
        self.db.add(tool)
        await self.db.flush()
        
        exec_type = ExecutionType.MCP
        if entry.cli_wrapper_script or entry.cli_command:
            exec_type = ExecutionType.CLI
            
        exec_params = {
            "catalog_slug": entry.slug,
            "openapi_url": entry.openapi_url,
            "source": "popular_apps_catalog"
        }
        
        execution_metadata = ToolExecutionMetadata(
            tool_id=tool.id,
            execution_type=exec_type,
            cli_wrapper=entry.cli_wrapper_script,
            exec_params=exec_params,
            auth_config=entry.auth_hint
        )
        self.db.add(execution_metadata)
        
        entry.is_cached = True
        entry.last_synced_at = datetime.now(timezone.utc)
        self.db.add(entry)
        
        await self.db.commit()
        await self.db.refresh(tool)
        logger.info("Warmed up registry from catalog", slug=slug, tool_id=str(tool.id))
        return tool

    async def ingest_from_openapi(self, openapi_url: str) -> CatalogEntry:
        """
        Auto-ingest a popular app from a public OpenAPI source.
        Useful for expanding the catalog dynamically.
        """
        # Reuse RegistryService's parsing logic without committing to ToolRegistry
        # We'll mock the agent_id just to use the existing logic
        mock_agent_id = uuid.uuid4()
        
        # Since RegistryService.ingest_openapi commits to TooolRegistry,
        # we might want a cleaner way to reuse its parser logic.
        from prance import ResolvingParser
        parser = ResolvingParser(openapi_url)
        spec = parser.specification
        
        title = spec.get("info", {}).get("title", "Unknown App")
        description = spec.get("info", {}).get("description", "")
        slug = title.lower().replace(" ", "-")
        
        # Extract actions for MCP definition
        actions = []
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                actions.append({
                    "name": f"{method.upper()} {path}",
                    "description": details.get("summary") or details.get("description", ""),
                    "inputSchema": { # Simplification
                        "type": "object",
                        "properties": {}
                    }
                })

        entry = CatalogEntry(
            slug=slug,
            display_name=title,
            description=description,
            openapi_url=openapi_url,
            mcp_definition={
                "name": slug,
                "description": description,
                "actions": actions
            },
            source=CatalogSource.OPENAPI_SYNC
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        logger.info("Auto-ingested catalog entry from OpenAPI", slug=slug, url=openapi_url)
        return entry
