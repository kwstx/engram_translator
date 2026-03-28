import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.crypto import CryptoService
from app.core.security import create_engram_access_token, verify_engram_token
from app.db.models import ProviderCredential, CredentialType
from app.messaging.connectors.claude import ClaudeConnector
from app.messaging.connectors.base import BaseConnector
from app.services.credentials import CredentialService


class _DummyAsyncClient:
    def __init__(self, captured):
        self._captured = captured

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None, headers=None):
        self._captured["url"] = url
        self._captured["json"] = json
        self._captured["headers"] = headers or {}
        return _DummyResponse(self._captured["response_payload"])


class _DummyResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _DummySession:
    def add(self, obj):
        return None

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None


class _DummyConnector(BaseConnector):
    def __init__(self):
        super().__init__(name="DUMMY")

    def translate_to_tool(self, engram_task):
        return engram_task

    def translate_from_tool(self, tool_response):
        return tool_response

    async def call_tool(self, tool_request, db=None, user_id=None):
        return tool_request


def test_engram_access_token_expiration():
    token = create_engram_access_token(
        user_id=str(uuid4()),
        permissions={"tool_x": ["read"]},
        expires_delta=timedelta(seconds=-1),
    )
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        verify_engram_token(token)
    assert exc.value.status_code == 401
    assert "expired" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_oauth_refresh_updates_token_and_returns_new(monkeypatch):
    user_id = uuid4()
    credential = ProviderCredential(
        user_id=user_id,
        provider_name="claude",
        credential_type=CredentialType.OAUTH_TOKEN,
        encrypted_token=CryptoService.encrypt("old-access-token"),
        encrypted_refresh_token=CryptoService.encrypt("refresh-token"),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        credential_metadata={
            "token_url": "https://example.com/token",
            "client_id": "client-id",
            "client_secret": "client-secret",
        },
    )

    async def _fake_get_by_provider(db, uid, provider_name):
        return credential

    async def _fake_refresh(db, cred):
        cred.encrypted_token = CryptoService.encrypt("new-access-token")
        cred.encrypted_refresh_token = CryptoService.encrypt("new-refresh-token")
        cred.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        return cred

    monkeypatch.setattr(CredentialService, "get_credential_by_provider", _fake_get_by_provider)
    monkeypatch.setattr(CredentialService, "refresh_oauth_token", _fake_refresh)

    token = await CredentialService.get_active_token(_DummySession(), user_id, "claude")

    assert token == "new-access-token"
    assert "new-access-token" not in credential.encrypted_token
    assert "new-refresh-token" not in credential.encrypted_refresh_token


@pytest.mark.asyncio
async def test_refreshed_token_used_in_connector_call(monkeypatch):
    user_id = uuid4()
    credential = ProviderCredential(
        user_id=user_id,
        provider_name="claude",
        credential_type=CredentialType.OAUTH_TOKEN,
        encrypted_token=CryptoService.encrypt("old-access-token"),
        encrypted_refresh_token=CryptoService.encrypt("refresh-token"),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        credential_metadata={
            "token_url": "https://example.com/token",
            "client_id": "client-id",
            "client_secret": "client-secret",
        },
    )

    async def _fake_get_by_provider(db, uid, provider_name):
        return credential

    async def _fake_refresh(db, cred):
        cred.encrypted_token = CryptoService.encrypt("new-access-token")
        cred.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        return cred

    captured = {
        "response_payload": {
            "content": [{"type": "text", "text": "ok"}],
            "model": "claude-3-haiku-20240307",
            "usage": {"input_tokens": 1, "output_tokens": 1},
        }
    }

    monkeypatch.setattr(CredentialService, "get_credential_by_provider", _fake_get_by_provider)
    monkeypatch.setattr(CredentialService, "refresh_oauth_token", _fake_refresh)
    monkeypatch.setattr(
        "app.messaging.connectors.claude.httpx.AsyncClient",
        lambda *args, **kwargs: _DummyAsyncClient(captured),
    )

    connector = ClaudeConnector(api_key="engram-claude-key")
    tool_request = {"model": "claude-3-haiku-20240307", "messages": [{"role": "user", "content": "hi"}]}

    await connector.call_tool(tool_request, db=_DummySession(), user_id=str(user_id))

    assert captured["headers"]["x-api-key"] == "new-access-token"


def test_expired_provider_error_prompts_refresh():
    connector = _DummyConnector()
    result = connector.handle_error(Exception("Token expired; please refresh"))

    assert result["error_type"] == "ExpiredTokenError"
    assert result["action_required"] == "REFRESH_CREDENTIALS"
