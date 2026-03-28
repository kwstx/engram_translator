from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from app.db.session import get_session
from app.db.models import CredentialType
from app.services.credentials import CredentialService
from app.core.security import get_current_principal
from pydantic import BaseModel
from uuid import UUID
import structlog
from app.core.logging import bind_context

router = APIRouter()
logger = structlog.get_logger(__name__)

from datetime import datetime

class CredentialSaveRequest(BaseModel):
    provider_name: str
    token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    credential_type: CredentialType = CredentialType.API_KEY
    metadata: Dict[str, Any] = {}

class CredentialResponse(BaseModel):
    id: UUID
    provider_name: str
    credential_type: CredentialType
    expires_at: Optional[datetime] = None
    # We do NOT return the token for security reasons

@router.post("/", response_model=CredentialResponse)
async def save_credential(
    request: CredentialSaveRequest,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal)
):
    """
    Securely stores a provider credential (API key or token) for the current user.
    The token is encrypted at rest using Fernet.
    """
    user_id = UUID(principal["sub"])
    bind_context(user_id=str(user_id))
    cred = await CredentialService.save_credential(
        db, 
        user_id, 
        request.provider_name.lower(), 
        request.token, 
        request.credential_type,
        refresh_token=request.refresh_token,
        expires_at=request.expires_at,
        metadata=request.metadata
    )
    logger.info(
        "Provider credential saved",
        user_id=str(user_id),
        provider=request.provider_name.lower(),
        credential_type=str(request.credential_type),
        has_refresh_token=bool(request.refresh_token),
    )
    return cred

@router.get("/", response_model=List[CredentialResponse])
async def list_credentials(
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal)
):
    """
    Lists all stored provider identities for the current user.
    """
    user_id = UUID(principal["sub"])
    bind_context(user_id=str(user_id))
    creds = await CredentialService.get_credentials(db, user_id)
    logger.info("Provider credentials listed", user_id=str(user_id), count=len(creds))
    return creds

@router.delete("/{provider_name}")
async def delete_credential(
    provider_name: str,
    db: AsyncSession = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal)
):
    """
    Removes a provider credential for the current user.
    """
    user_id = UUID(principal["sub"])
    bind_context(user_id=str(user_id))
    success = await CredentialService.delete_credential(db, user_id, provider_name.lower())
    if not success:
        logger.warning("Provider credential delete failed: not found", user_id=str(user_id), provider=provider_name.lower())
        raise HTTPException(status_code=404, detail="Credential not found")
    logger.info("Provider credential deleted", user_id=str(user_id), provider=provider_name.lower())
    return {"status": "deleted"}
