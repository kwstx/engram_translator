"""
DB models for the lightweight popular-apps catalog.

CatalogEntry stores pre-seeded dual wrappers (MCP definition + CLI command)
for well-known services.  They are *cache accelerators*: when the router
encounters a tool that matches a catalog slug, it can skip the full
auto-generation pipeline and use the pre-baked wrapper immediately, while
the self-healing loop still validates / patches it in the background.

CatalogSubmission records community PR-style contributions that await
review before promotion to the catalog.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, JSON
from sqlmodel import Field, SQLModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CatalogSource(str, enum.Enum):
    """Where a catalog entry originated."""
    SEED = "SEED"          # shipped with Engram
    OPENAPI_SYNC = "OPENAPI_SYNC"  # auto-ingested from public OpenAPI
    COMMUNITY = "COMMUNITY"        # accepted community submission


class SubmissionStatus(str, enum.Enum):
    """Lifecycle of a community submission."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ---------------------------------------------------------------------------
# CatalogEntry — the pre-seeded dual wrapper
# ---------------------------------------------------------------------------

class CatalogEntry(SQLModel, table=True):
    """
    A lightweight, pre-baked wrapper for a popular external service.

    Design philosophy:
      • Acts as a cache warm-up for the universal auto-generation pipeline.
      • Contains both an MCP tool definition AND a ready-to-use CLI
        command/script so the router can serve the tool instantly on first
        request without waiting for spec parsing + LLM extraction.
      • The reconciliation / self-healing loop treats catalog entries
        identically to auto-generated ones — if the upstream API changes,
        the entry is patched automatically.
    """
    __tablename__ = "catalog_entries"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Human-readable slug, unique across the catalog (e.g. "github", "stripe")
    slug: str = Field(index=True, unique=True, nullable=False)

    # Display metadata
    display_name: str = Field(nullable=False)
    description: str = Field(default="", nullable=False)
    icon_url: Optional[str] = Field(default=None)
    category: str = Field(default="general", index=True, nullable=False)
    tags: List[str] = Field(default=[], sa_type=JSON)

    # --- Dual wrapper payload ---

    # MCP tool definition: JSON-serialisable dict following the MCP tool spec.
    # Contains name, description, inputSchema, etc.
    mcp_definition: Dict[str, Any] = Field(default={}, sa_type=JSON)

    # CLI command template: either a raw shell command string or a small
    # Python script that wraps the service.
    cli_command: Optional[str] = Field(default=None)
    cli_wrapper_script: Optional[str] = Field(default=None)

    # Full OpenAPI / spec URL so the self-healing loop can re-validate.
    openapi_url: Optional[str] = Field(default=None)

    # Auth requirements hint (not credentials — just what type is needed)
    auth_hint: Dict[str, Any] = Field(default={}, sa_type=JSON)

    # Provenance
    source: CatalogSource = Field(default=CatalogSource.SEED, index=True, nullable=False)
    upstream_version: Optional[str] = Field(default=None)

    # Whether the entry has been promoted to the live tool registry cache
    is_cached: bool = Field(default=False, index=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    last_synced_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )


# ---------------------------------------------------------------------------
# CatalogSubmission — community PR-style contributions
# ---------------------------------------------------------------------------

class CatalogSubmission(SQLModel, table=True):
    """
    A pending community submission for a new catalog entry.

    Backed by a Git-style workflow: submissions are stored in the DB and
    can optionally be mirrored to a Git repo for review.  Once approved
    they are promoted to CatalogEntry.
    """
    __tablename__ = "catalog_submissions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Submitter info
    submitted_by: str = Field(nullable=False)  # email or agent ID
    submission_message: str = Field(default="", nullable=False)

    # Proposed wrapper payload (same shape as CatalogEntry)
    slug: str = Field(index=True, nullable=False)
    display_name: str = Field(nullable=False)
    description: str = Field(default="", nullable=False)
    category: str = Field(default="general", nullable=False)
    tags: List[str] = Field(default=[], sa_type=JSON)

    mcp_definition: Dict[str, Any] = Field(default={}, sa_type=JSON)
    cli_command: Optional[str] = Field(default=None)
    cli_wrapper_script: Optional[str] = Field(default=None)
    openapi_url: Optional[str] = Field(default=None)
    auth_hint: Dict[str, Any] = Field(default={}, sa_type=JSON)

    # Review state
    status: SubmissionStatus = Field(
        default=SubmissionStatus.PENDING, index=True, nullable=False
    )
    reviewer_notes: Optional[str] = Field(default=None)
    reviewed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
