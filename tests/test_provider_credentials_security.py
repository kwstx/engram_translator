import pytest
from uuid import uuid4

from app.db.models import CredentialType
from app.services.credentials import CredentialService


class FakeAsyncSession:
    def __init__(self):
        self.store = []

    def add(self, obj):
        if obj not in self.store:
            self.store.append(obj)

    async def delete(self, obj):
        self.store = [item for item in self.store if item is not obj]

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None


@pytest.mark.asyncio
async def test_provider_credentials_encrypted_and_removed(monkeypatch):
    db = FakeAsyncSession()
    user_id = uuid4()

    async def _get_by_provider(db_session, uid, provider_name):
        for item in db.store:
            if item.user_id == uid and item.provider_name == provider_name:
                return item
        return None

    monkeypatch.setattr(CredentialService, "get_credential_by_provider", _get_by_provider)

    # Simulate connecting Slack via API key
    slack_token = "xoxb-test-slack-token"
    slack_cred = await CredentialService.save_credential(
        db,
        user_id,
        "slack",
        slack_token,
        CredentialType.API_KEY,
    )

    # "Direct DB read" should not reveal the plaintext token
    raw_slack_token = slack_cred.encrypted_token
    assert raw_slack_token != slack_token
    assert slack_token not in raw_slack_token

    # Simulate connecting Claude via OAuth
    claude_token = "oauth-token-abc"
    claude_refresh = "refresh-token-xyz"
    claude_cred = await CredentialService.save_credential(
        db,
        user_id,
        "claude",
        claude_token,
        CredentialType.OAUTH_TOKEN,
        refresh_token=claude_refresh,
        metadata={"token_url": "https://example.com/token", "client_id": "test", "client_secret": "secret"},
    )

    raw_claude_token = claude_cred.encrypted_token
    raw_claude_refresh = claude_cred.encrypted_refresh_token
    assert raw_claude_token != claude_token
    assert claude_token not in raw_claude_token
    assert raw_claude_refresh != claude_refresh
    assert claude_refresh not in raw_claude_refresh

    # Disconnect Slack and ensure credential is removed
    deleted = await CredentialService.delete_credential(db, user_id, "slack")
    assert deleted is True
    assert await _get_by_provider(db, user_id, "slack") is None
