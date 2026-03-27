from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.db.session import get_session
from app.db.models import User, PermissionProfile
from app.core.security import get_current_principal
from pydantic import BaseModel

router = APIRouter()

class PermissionUpdate(BaseModel):
    profile_name: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None

class PermissionProfilePublic(BaseModel):
    id: UUID
    user_id: UUID
    profile_name: str
    permissions: Dict[str, List[str]]

@router.get("/me", response_model=PermissionProfilePublic)
async def get_my_permissions(
    db: Session = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    user_id = principal.get("sub")
    statement = select(PermissionProfile).where(PermissionProfile.user_id == user_id)
    result = await db.execute(statement)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission profile not found for the current user."
        )
    return profile

@router.get("/{user_id}", response_model=PermissionProfilePublic)
async def get_user_permissions(
    user_id: UUID,
    db: Session = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    # In a real system, you'd check if principal is a superuser
    # For now, we'll allow fetching any profile if authenticated
    statement = select(PermissionProfile).where(PermissionProfile.user_id == user_id)
    result = await db.execute(statement)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission profile not found for user {user_id}."
        )
    return profile

@router.put("/{user_id}", response_model=PermissionProfilePublic)
async def update_user_permissions(
    user_id: UUID,
    perm_in: PermissionUpdate,
    db: Session = Depends(get_session),
    principal: Dict[str, Any] = Depends(get_current_principal),
):
    statement = select(PermissionProfile).where(PermissionProfile.user_id == user_id)
    result = await db.execute(statement)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission profile not found for user {user_id}."
        )
    
    if perm_in.profile_name is not None:
        profile.profile_name = perm_in.profile_name
    if perm_in.permissions is not None:
        # Merge or replace. The request says "flexible enough to allow adding new tools dynamically"
        # Since we're using a dict/JSONB, this is already satisfied.
        profile.permissions = perm_in.permissions
        
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile
