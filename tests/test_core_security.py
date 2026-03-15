import pytest
import jwt
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from app.core.security import get_current_principal, _extract_scopes, _get_verification_key

def test_extract_scopes_string():
    payload = {"scope": "read write  test"}
    assert _extract_scopes(payload) == ["read", "write", "test"]

def test_extract_scopes_list():
    payload = {"scopes": ["read", "write"]}
    assert _extract_scopes(payload) == ["read", "write"]

def test_extract_scopes_empty():
    assert _extract_scopes({}) == []

@patch("app.core.security.settings")
def test_get_verification_key_hs(mock_settings):
    mock_settings.AUTH_JWT_ALGORITHM = "HS256"
    mock_settings.AUTH_JWT_SECRET = "secret"
    assert _get_verification_key() == "secret"

@patch("app.core.security.settings")
def test_get_verification_key_rs(mock_settings):
    mock_settings.AUTH_JWT_ALGORITHM = "RS256"
    mock_settings.AUTH_JWT_PUBLIC_KEY = "pubkey"
    assert _get_verification_key() == "pubkey"

@pytest.mark.asyncio
@patch("app.core.security.jwt.decode")
@patch("app.core.security._get_verification_key")
async def test_get_current_principal_valid(mock_get_key, mock_decode):
    mock_get_key.return_value = "key"
    mock_decode.return_value = {"aud": "aud", "iss": "iss", "exp": 123, "scope": "test:scope"}
    
    scopes = SecurityScopes(scopes=["test:scope"])
    result = await get_current_principal(scopes, token="valid_token")
    
    assert result["scope"] == "test:scope"

@pytest.mark.asyncio
@patch("app.core.security.jwt.decode")
@patch("app.core.security._get_verification_key")
async def test_get_current_principal_invalid_token(mock_get_key, mock_decode):
    mock_get_key.return_value = "key"
    mock_decode.side_effect = jwt.PyJWTError()
    
    scopes = SecurityScopes()
    with pytest.raises(HTTPException) as exc:
        await get_current_principal(scopes, token="invalid")
    assert exc.value.status_code == 401

@pytest.mark.asyncio
@patch("app.core.security.jwt.decode")
@patch("app.core.security._get_verification_key")
async def test_get_current_principal_insufficient_scope(mock_get_key, mock_decode):
    mock_get_key.return_value = "key"
    mock_decode.return_value = {"aud": "aud", "iss": "iss", "exp": 123, "scope": "read"}
    
    scopes = SecurityScopes(scopes=["write"])
    with pytest.raises(HTTPException) as exc:
        await get_current_principal(scopes, token="valid")
    assert exc.value.status_code == 403
