import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.main import app
from app.db.session import get_session
from app.core.security import get_current_principal
from app.db.models import AgentRegistry, Task, TaskStatus, AgentMessage, AgentMessageStatus

# Bypassing the security check for tests
async def override_get_current_principal():
    return {"sub": "test_user", "scope": "translate:a2a translate:beta"}

app.dependency_overrides[get_current_principal] = override_get_current_principal

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db():
    session = AsyncMock()
    return session

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Agent Translator Middleware is Online"

@pytest.mark.asyncio
async def test_register_agent(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    agent_data = {
        "agent_id": str(uuid4()),
        "name": "Test Agent",
        "endpoint_url": "http://test",
        "supported_protocols": ["A2A"]
    }
    
    # TestClient for sync calls, but the endpoint is async. 
    # FastAPI handles this internally by running async endpoints in a loop.
    response = client.post("/api/v1/register", json=agent_data)
    
    assert response.status_code == 200
    assert mock_session.commit.called
    assert mock_session.add.called
    app.dependency_overrides.pop(get_session)

@pytest.mark.asyncio
async def test_discover_agents(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        AgentRegistry(name="A1", supported_protocols=["A2A"])
    ]
    mock_session.execute.return_value = mock_result
    
    # Mocking the contains operator which is PG-specific
    with patch("app.api.v1.endpoints.AgentRegistry.supported_protocols") as mock_protocols:
        # Return a valid SQL expression (dummy)
        mock_protocols.contains.return_value = (AgentRegistry.id != None)
        response = client.get("/api/v1/discover?protocol=A2A")
        assert response.status_code == 200
        assert len(response.json()) == 1
    app.dependency_overrides.pop(get_session)

@pytest.mark.asyncio
async def test_enqueue_task(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    task_request = {
        "source_message": {"hello": "world"},
        "source_protocol": "A2A",
        "target_protocol": "MCP",
        "target_agent_id": str(uuid4())
    }
    
    response = client.post("/api/v1/queue/enqueue", json=task_request)
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert mock_session.commit.called
    app.dependency_overrides.pop(get_session)

@pytest.mark.asyncio
async def test_poll_agent_messages_none(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    with patch("app.api.v1.endpoints.lease_agent_message", new_callable=AsyncMock) as mock_lease:
        mock_lease.return_value = None
        agent_id = uuid4()
        response = client.post(f"/api/v1/agents/{agent_id}/messages/poll")
        assert response.status_code == 204
    app.dependency_overrides.pop(get_session)

@pytest.mark.asyncio
async def test_translate_unauthenticated_logic(client):
    # translate_message is basically a placeholder in current code
    # But it uses require_scopes(["translate:a2a"])
    request_data = {
        "source_agent": "A",
        "target_agent": "B",
        "payload": {"data": 1}
    }
    response = client.post("/api/v1/translate", json=request_data)
    assert response.status_code == 200
    assert response.json()["status"] == "pending"

@pytest.mark.asyncio
async def test_discover_agents_post(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    # Mock mapping results or empty
    mock_mapping_result = MagicMock()
    mock_mapping_result.scalars.return_value.all.return_value = []
    
    # Mock agent registry results
    mock_agent_result = MagicMock()
    mock_agent_result.scalars.return_value.all.return_value = [
        AgentRegistry(name="A1", supported_protocols=["A2A"], semantic_tags=["tag1"])
    ]
    
    mock_session.execute.side_effect = [mock_mapping_result, mock_agent_result]
    
    discovery_request = {
        "protocols": ["A2A"],
        "semantic_tags": ["tag1"]
    }
    
    with patch("app.api.v1.discovery.AgentRegistry.supported_protocols") as mock_proto, \
         patch("app.api.v1.discovery.AgentRegistry.semantic_tags") as mock_tags:
        # Return valid SQL expressions
        mock_proto.overlap.return_value = (AgentRegistry.id != None)
        mock_tags.overlap.return_value = (AgentRegistry.id != None)
        
        response = client.post("/api/v1/discovery/", json=discovery_request)
        assert response.status_code == 200
        assert len(response.json()) == 1
    app.dependency_overrides.pop(get_session)

@pytest.mark.asyncio
async def test_get_collaborators_api(client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    
    with patch("app.services.discovery.DiscoveryService.find_collaborators", new_callable=AsyncMock) as mock_find:
        agent = AgentRegistry(agent_id=str(uuid4()), endpoint_url="http://test", supported_protocols=["A2A"], is_active=True)
        mock_find.return_value = [{
            "agent": agent,
            "compatibility_score": 0.8,
            "shared_protocols": ["A2A"],
            "mappable_protocols": []
        }]
        
        response = client.get("/api/v1/discovery/collaborators?protocols=A2A")
        assert response.status_code == 200
        assert response.json()[0]["compatibility_score"] == 0.8
    app.dependency_overrides.pop(get_session)
