from typing import List, Optional, Dict, Any

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scopes={
        "translate:a2a": "Translate messages using A2A protocol scope.",
    },
)


def _get_verification_key() -> str:
    if settings.AUTH_JWT_ALGORITHM.startswith("HS"):
        if not settings.AUTH_JWT_SECRET:
            raise RuntimeError("AUTH_JWT_SECRET is required for HS* algorithms.")
        return settings.AUTH_JWT_SECRET
    if not settings.AUTH_JWT_PUBLIC_KEY:
        raise RuntimeError("AUTH_JWT_PUBLIC_KEY is required for RS*/ES* algorithms.")
    return settings.AUTH_JWT_PUBLIC_KEY


def _extract_scopes(payload: Dict[str, Any]) -> List[str]:
    scope_val = payload.get("scope")
    if isinstance(scope_val, str):
        return [s for s in scope_val.split(" ") if s]
    scopes_val = payload.get("scopes")
    if isinstance(scopes_val, list):
        return [str(s) for s in scopes_val]
    return []


async def get_current_principal(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    key = _get_verification_key()
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.AUTH_JWT_ALGORITHM],
            audience=settings.AUTH_AUDIENCE,
            issuer=settings.AUTH_ISSUER,
            options={"require": ["exp", "iss", "aud"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token.") from exc

    token_scopes = _extract_scopes(payload)
    required_scopes = list(security_scopes.scopes)
    if required_scopes and not set(required_scopes).issubset(set(token_scopes)):
        raise HTTPException(status_code=403, detail="Insufficient scope for this resource.")

    return payload


def require_scopes(scopes: List[str]):
    return Security(get_current_principal, scopes=scopes)
