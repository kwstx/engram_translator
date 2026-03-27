import sys
from unittest.mock import MagicMock
sys.modules["pyswip"] = MagicMock()

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.main import app
from app.db.session import get_session
from app.db.models import User

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_signup_flow(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    # Mock user exists check (return None for first call)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    signup_data = {
        "email": "testuser@example.com",
        "password": "strongpassword123",
        "user_metadata": {"profile": "standard"}
    }
    
    # We need to simulate the refresh call assigning an ID
    def mock_refresh(obj):
        obj.id = uuid4()
    mock_session.refresh.side_effect = mock_refresh
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    
    assert response.status_code == 201
    assert response.json()["email"] == signup_data["email"]
    assert "id" in response.json()
    
    app.dependency_overrides.pop(get_session)

@pytest.mark.asyncio
async def test_login_flow(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    from app.core.security import get_password_hash
    password = "strongpassword123"
    hashed = get_password_hash(password)
    
    # Mock user lookup
    mock_user = User(
        id=uuid4(),
        email="testuser@example.com",
        hashed_password=hashed,
        is_active=True
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_session.execute.return_value = mock_result
    
    login_data = {
        "username": "testuser@example.com",
        "password": password
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    app.dependency_overrides.pop(get_session)
