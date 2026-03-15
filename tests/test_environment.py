import pytest
from httpx import AsyncClient
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_health_check():
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Agent Translator Middleware is Online", "version": "0.1.0"}

@pytest.mark.asyncio
async def test_translate_endpoint_mock():
    # This is a smoke test for the router
    from httpx import ASGITransport
    payload = {
        "source_message": {"intent": "greet"},
        "source_protocol": "mcp",
        "target_protocol": "a2a"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(f"{settings.API_V1_STR}/translate", json=payload)
    
    # We expect 401 if auth is on, or 200 if it's open/mocked
    # Adjust based on current security implementation
    assert response.status_code in [200, 401]
