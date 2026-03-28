
import sys
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4, UUID
import jwt
from datetime import timedelta

import os

# Disable Redis and provide necessary settings for tests
os.environ["REDIS_ENABLED"] = "false"
os.environ["AUTH_JWT_SECRET"] = "test-secret-that-is-long-enough-for-hs256"
os.environ["AUTH_ISSUER"] = "https://auth.example.com/"
os.environ["AUTH_AUDIENCE"] = "translator-middleware"
# Don't set DATABASE_URL, let it fall back to default but mock initiation

# SIMPLIFIED ROBUST MOCKING
for mod_name in ["pyswip", "owlready2", "pyDatalog", "pyswip.core"]:
    mock = MagicMock()
    sys.modules[mod_name] = mock
    # Ensure attributes used in 'from mod import attr' are present
    if mod_name == "pyswip":
        mock.Prolog = MagicMock
    elif mod_name == "owlready2":
        mock.get_ontology = MagicMock
        mock.World = MagicMock
    elif mod_name == "pyDatalog":
        mock.pyDatalog = mock

# Patch app.db.session.init_db as soon as it's imported
with patch("app.db.session.init_db", AsyncMock()):
    from app.main import app
from app.db.session import get_session
from app.db.models import User, PermissionProfile
from app.core.security import get_current_principal, create_engram_access_token
from app.core.config import settings
from app.messaging.orchestrator import Orchestrator

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_permission_profile_full_flow(client):
    """
    Verified Plan:
    1. Create users Alice and Bob with different permission levels.
    2. Verify initial token generation reflects their database profiles.
    3. Simulate tasks and verify that Orchestrator blocks unauthorized actions.
    4. Update a permission profile and verify it takes effect on the next token generation.
    """
    
    # --- 1. SETUP USERS AND PROFILES ---
    alice_id = uuid4()
    bob_id = uuid4()
    
    alice_profile = PermissionProfile(
        user_id=alice_id,
        profile_name="Alice-Core",
        permissions={"CLAUDE": ["execute"], "SLACK": ["read", "write"]}
    )
    
    bob_profile = PermissionProfile(
        user_id=bob_id,
        profile_name="Bob-Research",
        permissions={"PERPLEXITY": ["execute"]}
    )

    # Mock DB Session
    mock_db = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_db
    
    # Mock return for Alice's profile lookup
    mock_result_alice = MagicMock()
    mock_result_alice.scalars.return_value.first.return_value = alice_profile
    
    # Mock return for Bob's profile lookup
    mock_result_bob = MagicMock()
    mock_result_bob.scalars.return_value.first.return_value = bob_profile
    
    # --- 2. VERIFY EAT GENERATION ---
    
    # alice's token
    app.dependency_overrides[get_current_principal] = lambda: {"sub": str(alice_id), "scope": "translate:a2a"}
    mock_db.execute.return_value = mock_result_alice
    
    resp_alice = client.post("/api/v1/auth/tokens/generate-eat")
    assert resp_alice.status_code == 200
    alice_eat = resp_alice.json()["eat"]
    
    # bob's token
    app.dependency_overrides[get_current_principal] = lambda: {"sub": str(bob_id), "scope": "translate:a2a"}
    mock_db.execute.return_value = mock_result_bob
    
    resp_bob = client.post("/api/v1/auth/tokens/generate-eat")
    assert resp_bob.status_code == 200
    bob_eat = resp_bob.json()["eat"]
    
    # --- 3. VERIFY TOKEN SCOPES ---
    
    payload_alice = jwt.decode(alice_eat, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM], audience=settings.AUTH_AUDIENCE)
    assert "CLAUDE" in payload_alice["allowed_tools"]
    assert "SLACK" in payload_alice["allowed_tools"]
    assert "PERPLEXITY" not in payload_alice["allowed_tools"]
    
    payload_bob = jwt.decode(bob_eat, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM], audience=settings.AUTH_AUDIENCE)
    assert "PERPLEXITY" in payload_bob["allowed_tools"]
    assert "CLAUDE" not in payload_bob["allowed_tools"]
    
    # --- 4. TEST ORCHESTRATOR BLOCKING (SIMULATION) ---
    
    orchestrator = Orchestrator()
    # Mock connector registry to bypass actual network calls
    orchestrator.connector_registry.has_connector = MagicMock(return_value=True)
    orchestrator.connector_registry.get_connector = MagicMock()
    orchestrator.connector_registry.get_connector.return_value.execute = AsyncMock(return_value={"status": "success"})
    
    # Alice tries CLAUDE (Allowed)
    result = await orchestrator.handoff_async({"msg": "hi"}, "A2A", "CLAUDE", eat=alice_eat)
    assert result.translated_message["status"] == "success"
    
    # Alice tries PERPLEXITY (Blocked)
    from app.core.exceptions import HandoffAuthorizationError
    with pytest.raises(HandoffAuthorizationError) as exc:
        await orchestrator.handoff_async({"msg": "hi"}, "A2A", "PERPLEXITY", eat=alice_eat)
    assert "does not authorize handoff to tool/protocol 'PERPLEXITY'" in str(exc.value)
    
    # Bob tries PERPLEXITY (Allowed)
    result = await orchestrator.handoff_async({"search": "test"}, "A2A", "PERPLEXITY", eat=bob_eat)
    assert result.translated_message["status"] == "success"
    
    # Bob tries SLACK (Blocked)
    with pytest.raises(HandoffAuthorizationError) as exc:
        await orchestrator.handoff_async({"msg": "hi"}, "A2A", "SLACK", eat=bob_eat)
    assert "does not authorize handoff to tool/protocol 'SLACK'" in str(exc.value)

    # --- 5. TEST REAL-TIME / NEXT SESSION UPDATE ---
    
    # Update Alice's profile to add PERPLEXITY
    alice_profile.permissions["PERPLEXITY"] = ["execute"]
    
    # Generate NEW token for Alice
    app.dependency_overrides[get_current_principal] = lambda: {"sub": str(alice_id), "scope": "translate:a2a"}
    mock_db.execute.return_value = mock_result_alice # Alice's profile now has PERPLEXITY
    
    resp_alice_updated = client.post("/api/v1/auth/tokens/generate-eat")
    alice_eat_updated = resp_alice_updated.json()["eat"]
    
    # Verify Alice can now access PERPLEXITY with the NEW token
    result_updated = await orchestrator.handoff_async({"msg": "hi"}, "A2A", "PERPLEXITY", eat=alice_eat_updated)
    assert result_updated.translated_message["status"] == "success"
    
    # Verify the OLD token is still blocked (unless revoked, which is expected JWT behavior)
    with pytest.raises(HandoffAuthorizationError):
        await orchestrator.handoff_async({"msg": "hi"}, "A2A", "PERPLEXITY", eat=alice_eat)

    # cleanup overrides
    app.dependency_overrides.clear()

if __name__ == "__main__":
    import asyncio
    
    async def run_standalone():
        print("Starting standalone test...")
        # Don't use 'with' to avoid triggering lifespan (which calls init_db/postgres)
        client_instance = TestClient(app)
        await test_permission_profile_full_flow(client_instance)
        print("Standalone test completed SUCCESS-FULLY!")

    try:
        asyncio.run(run_standalone())
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
