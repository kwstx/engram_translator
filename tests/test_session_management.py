import sys
from unittest.mock import AsyncMock, MagicMock

sys.modules["pyswip"] = MagicMock()

import jwt
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models import User
from app.db.session import get_session

import app.core.redis_client as redis_client
import app.core.security as security
import app.services.session as session_service


class FakeRedis:
    def __init__(self):
        self._now = 0.0
        self._data = {}
        self._expires = {}
        self._sets = {}
        self._set_expires = {}

    def advance(self, seconds: float):
        self._now += seconds

    def _coerce_ttl(self, ttl):
        if hasattr(ttl, "total_seconds"):
            return int(ttl.total_seconds())
        return int(ttl)

    def _is_expired(self, key: str, is_set: bool = False) -> bool:
        expires = self._set_expires if is_set else self._expires
        store = self._sets if is_set else self._data
        if key in expires and self._now >= expires[key]:
            expires.pop(key, None)
            store.pop(key, None)
            return True
        return False

    def setex(self, key, ttl, value):
        self._data[key] = value
        self._expires[key] = self._now + self._coerce_ttl(ttl)

    def expire(self, key, ttl):
        seconds = self._coerce_ttl(ttl)
        if key in self._data:
            self._expires[key] = self._now + seconds
            return True
        if key in self._sets:
            self._set_expires[key] = self._now + seconds
            return True
        return False

    def get(self, key):
        if key in self._data:
            if self._is_expired(key):
                return None
            return self._data[key]
        return None

    def delete(self, key):
        removed = 0
        if key in self._data:
            self._data.pop(key, None)
            self._expires.pop(key, None)
            removed += 1
        if key in self._sets:
            self._sets.pop(key, None)
            self._set_expires.pop(key, None)
            removed += 1
        return removed

    def sadd(self, key, *values):
        if key not in self._sets:
            self._sets[key] = set()
        before = len(self._sets[key])
        self._sets[key].update(values)
        return len(self._sets[key]) - before

    def srem(self, key, *values):
        if key not in self._sets:
            return 0
        removed = 0
        for val in values:
            if val in self._sets[key]:
                self._sets[key].remove(val)
                removed += 1
        return removed

    def smembers(self, key):
        if key in self._sets:
            if self._is_expired(key, is_set=True):
                return set()
            return set(self._sets[key])
        return set()

    def exists(self, key):
        if key in self._data:
            if self._is_expired(key):
                return 0
            return 1
        if key in self._sets:
            if self._is_expired(key, is_set=True):
                return 0
            return 1
        return 0


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_client, "get_redis_client", lambda: fake)
    monkeypatch.setattr(session_service, "get_redis_client", lambda: fake)
    monkeypatch.setattr(security, "get_redis_client", lambda: fake)
    return fake


@pytest.fixture
def auth_user():
    password = "strongpassword123"
    hashed = get_password_hash(password)
    user = User(
        id=uuid4(),
        email="testuser@example.com",
        hashed_password=hashed,
        is_active=True,
    )
    return user, password


@pytest.fixture
def mock_db_session(auth_user):
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = auth_user[0]
    mock_session.execute.return_value = mock_result
    app.dependency_overrides[get_session] = lambda: mock_session
    yield mock_session
    app.dependency_overrides.pop(get_session)


@pytest.fixture
def short_session_ttl(monkeypatch):
    original = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 1)
    yield
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", original)


def _login(client, email, password):
    response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _decode_token(token):
    return jwt.decode(
        token,
        settings.AUTH_JWT_SECRET,
        algorithms=[settings.AUTH_JWT_ALGORITHM],
        audience=settings.AUTH_AUDIENCE,
        issuer=settings.AUTH_ISSUER,
        options={"verify_exp": False},
    )


def test_session_valid_within_window(client, fake_redis, mock_db_session, auth_user, short_session_ttl):
    user, password = auth_user
    token = _login(client, user.email, password)

    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(token))
    assert response.status_code == 200
    assert len(response.json()) == 1

    fake_redis.advance(30)
    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_session_expires_and_requires_relogin(client, fake_redis, mock_db_session, auth_user, short_session_ttl):
    user, password = auth_user
    token = _login(client, user.email, password)

    fake_redis.advance(61)
    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(token))
    assert response.status_code == 401
    assert "Session expired or revoked" in response.json()["detail"]

    new_token = _login(client, user.email, password)
    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(new_token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_expired_session_token_denied(client, fake_redis, mock_db_session, auth_user):
    user, password = auth_user
    token = _login(client, user.email, password)
    payload = _decode_token(token)
    fake_redis.delete(f"session:{payload['sid']}")

    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(token))
    assert response.status_code == 401
    assert "Session expired or revoked" in response.json()["detail"]


def test_logout_revokes_token(client, fake_redis, mock_db_session, auth_user):
    user, password = auth_user
    token = _login(client, user.email, password)

    response = client.post("/api/v1/auth/logout", headers=_auth_headers(token))
    assert response.status_code == 200

    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(token))
    assert response.status_code == 401
    assert "revoked" in response.json()["detail"]


def test_multiple_concurrent_sessions_tracking(client, fake_redis, mock_db_session, auth_user):
    user, password = auth_user
    token_a = _login(client, user.email, password)
    token_b = _login(client, user.email, password)

    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(token_b))
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 2

    sid_a = _decode_token(token_a)["sid"]
    sid_b = _decode_token(token_b)["sid"]
    session_ids = {entry["sid"] for entry in sessions}
    assert {sid_a, sid_b}.issubset(session_ids)

    response = client.post("/api/v1/auth/logout", headers=_auth_headers(token_a))
    assert response.status_code == 200

    response = client.get("/api/v1/auth/sessions", headers=_auth_headers(token_b))
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 1
    assert sessions[0]["sid"] == sid_b
