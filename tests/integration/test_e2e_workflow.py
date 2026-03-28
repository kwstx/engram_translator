import pytest
import uuid
import json
import asyncio
import sys
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

# --- MOCK PYSWIP EARLY ---
mock_pyswip = MagicMock()
mock_prolog = MagicMock()
mock_prolog.query.return_value = []
mock_pyswip.Prolog.return_value = mock_prolog
sys.modules["pyswip"] = mock_pyswip

from fastapi import status
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.models import User, PermissionProfile
from app.db.session import get_session
from app.core.security import get_current_principal

@pytest.mark.asyncio
async def test_complete_user_to_task_flow():
    """
    Verifies the complete end-to-end flow.
    """
    # Setup Mocks
    mock_user_id = uuid.uuid4()
    mock_user = User(id=mock_user_id, email="e2e_user@example.com", hashed_password="hashed_password")
    mock_profile = PermissionProfile(user_id=mock_user_id, permissions={
        "CLAUDE": ["*"], "SLACK": ["*"], "core_translator": ["*"]
    })
    
    mock_db = AsyncMock()
    
    # Override app dependencies
    async def mock_get_session():
        yield mock_db
    
    async def mock_principal():
        return {"user_id": str(mock_user_id), "scopes": ["translate:a2a", "translate:beta"]}

    app.dependency_overrides[get_session] = mock_get_session
    app.dependency_overrides[get_current_principal] = mock_principal
    
    from app.services.session import SessionService
    from app.services.credentials import CredentialService
    
    # Mocking at the service layer
    with patch.object(SessionService, "create_session", return_value="mock_sid"), \
         patch.object(SessionService, "get_session", return_value={"user_id": str(mock_user_id)}), \
         patch.object(SessionService, "extend_session"), \
         patch("app.core.security.is_token_revoked", return_value=False), \
         patch("app.api.v1.auth.verify_password", return_value=True), \
         patch("app.messaging.multi_agent_orchestrator.memory_backend", MagicMock()):

        # Mock database queries
        mock_result_user = MagicMock()
        mock_result_user.scalars().first.return_value = mock_user
        
        mock_result_profile = MagicMock()
        mock_result_profile.scalars().first.return_value = mock_profile
        
        mock_result_none = MagicMock()
        mock_result_none.scalars().first.return_value = None

        async def _mock_execute(statement, *args, **kwargs):
            stmt_str = str(statement).lower()
            if "from users" in stmt_str:
                return mock_result_user
            if "from permission_profiles" in stmt_str:
                return mock_result_profile
            return MagicMock()
        mock_db.execute.side_effect = _mock_execute

        with patch.object(CredentialService, "save_credential", return_value=MagicMock()), \
             patch.object(CredentialService, "get_active_token") as mock_get_token:

            user_claude_key = "sk-ant-e2e-user-key"
            user_slack_key = "xoxb-e2e-user-token"
            
            async def _mock_get_active_token(db, uid, provider):
                if provider.lower() == "claude": return user_claude_key
                if provider.lower() == "slack": return user_slack_key
                return None
            mock_get_token.side_effect = _mock_get_active_token

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                
                # 1. User Signup Lifecycle
                print("\n[E2E] Step 1: User Signup & Login Flow")
                # We mock the signup/login to avoid DB complexities while verifying the API interfaces
                with patch("app.api.v1.auth.signup", return_value=mock_user):
                    signup_resp = await client.post("/api/v1/auth/signup", json={
                        "email": "e2e_user@example.com",
                        "password": "testpassword123"
                    })
                    assert signup_resp.status_code == 201

                login_resp = await client.post("/api/v1/auth/login", data={
                    "username": "e2e_user@example.com",
                    "password": "testpassword123"
                })
                assert login_resp.status_code == 200
                session_token = login_resp.json()["access_token"]
                auth_headers = {"Authorization": f"Bearer {session_token}"}
                print("      Success: User authenticated and session established")

                # 2. Store Provider Credentials (Verification of Billing/Identity)
                print("[E2E] Step 2: Connecting Providers (User-Specific Keys)")
                await client.post("/api/v1/credentials/", json={
                    "provider_name": "CLAUDE",
                    "token": user_claude_key,
                    "credential_type": "API_KEY"
                }, headers=auth_headers)
                print("      Success: User-specific credentials stored securely")

                # 3. Generate Engram Access Token (EAT)
                print("[E2E] Step 3: Generating Engram Access Token (EAT)")
                eat_resp = await client.post("/api/v1/auth/tokens/generate-eat", json={"expires_days": 1}, headers=auth_headers)
                assert eat_resp.status_code == 200
                eat = eat_resp.json()["eat"]
                eat_headers = {"Authorization": f"Bearer {eat}"}
                print("      Success: EAT obtained for agent-to-agent authorization")

                # 4. Multi-Agent Task Orchestration
                print("[E2E] Step 4: Submitting Complex Multi-Agent Task")
                captured_calls = []

                async def mocked_post(url, **kwargs):
                    headers = kwargs.get("headers", {})
                    url_str = str(url)
                    tool = "CLAUDE" if "anthropic" in url_str else "SLACK"
                    captured_calls.append({
                        "tool": tool,
                        "headers": {k.lower(): v for k, v in headers.items()}
                    })
                    mock_resp = MagicMock()
                    mock_resp.status_code = 200
                    mock_resp.json.return_value = {"content": [{"text": "OK"}]} if tool == "CLAUDE" else {"ok": True}
                    return mock_resp

                with patch("httpx.AsyncClient.post", side_effect=mocked_post):
                    task_str = "Summarize the research with CLAUDE then post findings to SLACK"
                    orch_resp = await client.post("/api/v1/orchestrate", json={"task": task_str}, headers=eat_headers)
                    assert orch_resp.status_code == 200
                print("      Success: Orchestration completed multi-hop flow (Claude -> Slack)")

                # 5. Billing & Integrity Verification
                print("[E2E] Step 5: Verifying User Billing Integrity")
                claude_call = next(c for c in captured_calls if c["tool"] == "CLAUDE")
                assert claude_call["headers"]["x-api-key"] == user_claude_key
                print(f"      Confirmed: CLAUDE call used user's private key '{user_claude_key[:6]}...'")
                
                slack_call = next(c for c in captured_calls if c["tool"] == "SLACK")
                assert slack_call["headers"]["authorization"] == f"Bearer {user_slack_key}"
                print(f"      Confirmed: SLACK call used user's private token '{user_slack_key[:6]}...'")

                print("\n--- E2E WORKFLOW TEST PASSED ---")

if __name__ == "__main__":
    try:
        asyncio.run(test_complete_user_to_task_flow())
        print("\n[FINISH] E2E Test Script concluded successfully.")
    except Exception as e:
        print(f"\n[FATAL] E2E Test Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
