import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.db.session import get_session
from app.catalog.models import CatalogEntry, CatalogSubmission, SubmissionStatus
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/catalog", tags=["Catalog"])
logger = structlog.get_logger(__name__)

@router.get("/entries", response_model=List[CatalogEntry])
async def list_catalog_entries(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """List popular apps in the catalog."""
    service = CatalogService(db)
    return await service.get_entries(category)

@router.get("/entries/{slug}", response_model=CatalogEntry)
async def get_catalog_entry(
    slug: str,
    db: AsyncSession = Depends(get_session)
):
    """Get details of a specific popular app."""
    service = CatalogService(db)
    entry = await service.get_entry_by_slug(slug)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.post("/submit", status_code=status.HTTP_201_CREATED, response_model=CatalogSubmission)
async def submit_to_catalog(
    submission: CatalogSubmission,
    db: AsyncSession = Depends(get_session)
):
    """Submit a new popular app to the catalog (community PR-style)."""
    service = CatalogService(db)
    return await service.submit_entry(submission)

@router.post("/promote/{submission_id}", response_model=CatalogEntry)
async def promote_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
):
    """Approve and promote a community submission to the catalog (Admin only)."""
    # In a real app, this would have admin role checks
    service = CatalogService(db)
    try:
        return await service.promote_submission(submission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/warm-up/{slug}", status_code=status.HTTP_201_CREATED)
async def warm_up_registry(
    slug: str,
    agent_id: uuid.UUID = Body(..., embed=True),
    db: AsyncSession = Depends(get_session)
):
    """
    Pre-populate the registry cache with a popular app wrapper.
    This enables instant discovery for common services.
    """
    service = CatalogService(db)
    tool = await service.warm_up_registry(slug, agent_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Catalog entry not found")
    return tool

@router.post("/ingest/openapi", status_code=status.HTTP_201_CREATED, response_model=CatalogEntry)
async def ingest_catalog_from_openapi(
    url: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_session)
):
    """Auto-ingest a popular app into the catalog from an OpenAPI URL."""
    service = CatalogService(db)
    return await service.ingest_from_openapi(url)
