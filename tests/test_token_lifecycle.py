import sys
from unittest.mock import MagicMock, patch, AsyncMock

# Absolute mock of pyswip
sys.modules["pyswip"] = MagicMock()

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import HTTPException

# Patch SemanticMapper to avoid ontology loading
from app.semantic.mapper import SemanticMapper
SemanticMapper.load_ontology = MagicMock(return_value=None)

from app.core.security import create_engram_access_token, verify_engram_token
from app.services.credentials import CredentialService
from app.db.models import ProviderCredential, CredentialType
from app.core.crypto import CryptoService
from app.core.exceptions import HandoffAuthorizationError
from app.messaging.connectors.base import BaseConnector

# Dummy concrete class for testing BaseConnector logic
class DemoConnector(BaseConnector):
    def translate_to_tool(self, e): return e
    def translate_from_tool(self, r): return r
    async def call_tool(self, r, db=None, uid=None): return {"status": "success"}

# Mock DB Session
class MockDBSession:
    def __init__(self, data=None):
        self.data = data or []
        self.committed = False
    
    def add(self, obj):
        if obj not in self.data:
            self.data.append(obj)
    
    async def commit(self):
        self.committed = True
        
    async def refresh(self, obj):
        pass
        
    async def execute(self, statement):
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = self.data[0] if self.data else None
        return mock_result

@pytest.mark.asyncio
async def test_engram_access_token_expiration():
    """Verify EAT expiration logic."""
    user_id = str(uuid4())
    token = create_engram_access_token(
        user_id, 
        permissions={"test": ["read"]}, 
        expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(HTTPException) as exc:
        verify_engram_token(token)
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_provider_token_auto_refresh(monkeypatch):
    """Verify automatic refresh of provider tokens."""
    db = MockDBSession()
    user_id = uuid4()
    
    # Setup expired credential
    cred = ProviderCredential(
        user_id=user_id,
        provider_name="test_provider",
        credential_type=CredentialType.OAUTH_TOKEN,
        encrypted_token=CryptoService.encrypt("old"),
        encrypted_refresh_token=CryptoService.encrypt("refresh"),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        credential_metadata={"token_url": "http://mock/token"}
    )
    db.data.append(cred)
    
    # Mock lookup
    monkeypatch.setattr(CredentialService, "get_credential_by_provider", AsyncMock(return_value=cred))
    
    # Mock refresh response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "new_access",
        "refresh_token": "new_refresh",
        "expires_in": 3600
    }
    
    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_resp)):
        token = await CredentialService.get_active_token(db, user_id, "test_provider")
        assert token == "new_access"
        assert db.committed is True

@pytest.mark.asyncio
async def test_connector_maps_expired_token_error():
    """Verify connector handle_error correctly flags expired tokens."""
    conn = DemoConnector(name="DEMO")
    
    # Simulator "token expired" error response from a tool
    error = Exception("API Error: Token has expired")
    result = conn.handle_error(error)
    
    assert result["engram_code"] == "AUTH_FAILURE"
    assert result["error_type"] == "ExpiredTokenError"
    assert result["action_required"] == "REFRESH_CREDENTIALS"

@pytest.mark.asyncio
async def test_refresh_failure_falls_back(monkeypatch):
    """Verify system doesn't crash if refresh fails, returns old token."""
    db = MockDBSession()
    user_id = uuid4()
    
    cred = ProviderCredential(
        user_id=user_id,
        provider_name="fail_provider",
        credential_type=CredentialType.OAUTH_TOKEN,
        encrypted_token=CryptoService.encrypt("expired_orig"),
        encrypted_refresh_token=CryptoService.encrypt("bad_refresh"),
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        credential_metadata={"token_url": "http://mock/token"}
    )
    
    monkeypatch.setattr(CredentialService, "get_credential_by_provider", AsyncMock(return_value=cred))
    
    with patch("httpx.AsyncClient.post", AsyncMock(side_effect=Exception("Network failure"))):
        token = await CredentialService.get_active_token(db, user_id, "fail_provider")
        assert token == "expired_orig"

