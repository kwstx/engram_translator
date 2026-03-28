import pytest
from uuid import uuid4
from fastapi import HTTPException
from fastapi.security import SecurityScopes
import jwt
from structlog.testing import capture_logs

from app.api.v1.tasks import list_tasks, get_task_status
from app.api.v1.credentials import CredentialResponse
from app.core.security import get_current_principal
from app.db.models import Task, TaskStatus, ProviderCredential, CredentialType
from app.messaging.connectors.base import BaseConnector
from app.core.config import settings


class FakeResult:
    def __init__(self, items):
        self._items = list(items)

    def scalars(self):
        return self

    def all(self):
        return list(self._items)

    def first(self):
        return self._items[0] if self._items else None


class FakeAsyncSession:
    def __init__(self, items):
        self._items = list(items)

    async def execute(self, stmt):
        return FakeResult(self._items)

    def add(self, obj):
        return None

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None


class DummyConnector(BaseConnector):
    def translate_to_tool(self, engram_task):
        return {}

    def translate_from_tool(self, tool_response):
        return {}

    async def call_tool(self, tool_request, db=None, user_id=None):
        return {}


@pytest.mark.asyncio
async def test_task_list_scoped_to_user():
    user_a = uuid4()
    user_b = uuid4()
    tasks = [
        Task(
            id=uuid4(),
            user_id=user_a,
            source_protocol="NL",
            target_protocol="MULTI_AGENT",
            source_message={"command": "task-a"},
            status=TaskStatus.PENDING,
        ),
        Task(
            id=uuid4(),
            user_id=user_b,
            source_protocol="NL",
            target_protocol="MULTI_AGENT",
            source_message={"command": "task-b"},
            status=TaskStatus.PENDING,
        ),
    ]
    session = FakeAsyncSession(tasks)
    result = await list_tasks(limit=10, db=session, principal={"sub": str(user_a)})
    assert len(result) == 1
    assert result[0].user_id == user_a


@pytest.mark.asyncio
async def test_task_status_denies_cross_user_access():
    user_a = uuid4()
    user_b = uuid4()
    task = Task(
        id=uuid4(),
        user_id=user_b,
        source_protocol="NL",
        target_protocol="MULTI_AGENT",
        source_message={"command": "task-b"},
        status=TaskStatus.PENDING,
    )
    session = FakeAsyncSession([task])
    with pytest.raises(HTTPException) as excinfo:
        await get_task_status(task.id, db=session, principal={"sub": str(user_a)})
    assert excinfo.value.status_code == 404


def test_credential_response_omits_tokens():
    cred = ProviderCredential(
        id=uuid4(),
        user_id=uuid4(),
        provider_name="slack",
        credential_type=CredentialType.API_KEY,
        encrypted_token="encrypted-token",
    )
    response = CredentialResponse.model_validate(cred)
    payload = response.model_dump()
    assert "encrypted_token" not in payload
    assert "encrypted_refresh_token" not in payload


@pytest.mark.asyncio
async def test_connector_token_lookup_scoped_to_user(monkeypatch):
    connector = DummyConnector(name="SLACK")
    user_a = uuid4()
    user_b = uuid4()

    async def _fake_get_active_token(db, uid, provider_name):
        if uid == user_a:
            return "token-a"
        if uid == user_b:
            return "token-b"
        return None

    monkeypatch.setattr(
        "app.services.credentials.CredentialService.get_active_token",
        _fake_get_active_token,
    )

    token_a = await connector.get_active_token(db=object(), user_id=str(user_a))
    token_b = await connector.get_active_token(db=object(), user_id=str(user_b))
    assert token_a == "token-a"
    assert token_b == "token-b"


@pytest.mark.asyncio
async def test_logs_do_not_include_tokens(monkeypatch):
    connector = DummyConnector(name="SLACK")
    user_id = uuid4()
    token_value = "super-secret-token"

    async def _fake_get_active_token(db, uid, provider_name):
        return token_value

    monkeypatch.setattr(
        "app.services.credentials.CredentialService.get_active_token",
        _fake_get_active_token,
    )

    with capture_logs() as logs:
        await connector.get_active_token(db=object(), user_id=str(user_id))

    assert all(token_value not in str(entry) for entry in logs)


@pytest.mark.asyncio
async def test_spoofed_token_rejected():
    bad_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "scope": "translate:a2a",
            "exp": 1893456000,
            "iss": settings.AUTH_ISSUER,
            "aud": settings.AUTH_AUDIENCE,
        },
        "wrong-secret",
        algorithm=settings.AUTH_JWT_ALGORITHM,
    )
    with pytest.raises(HTTPException) as excinfo:
        await get_current_principal(SecurityScopes(scopes=["translate:a2a"]), token=bad_token)
    assert excinfo.value.status_code == 401
