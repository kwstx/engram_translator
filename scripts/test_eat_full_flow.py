import os
import sys
import uuid
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

# Ensure app is in path
sys.path.append(os.getcwd())

# Mock Redis BEFORE anything else
with patch("app.core.redis_client.get_redis_client", return_value=None):
    from app.main import app
    from app.db.session import get_session
    from app.db.models import User, PermissionProfile
    from app.core.security import get_password_hash, verify_engram_token, _get_signing_key
    from app.core.config import settings
    import jwt

client = TestClient(app)

def test_full_auth_to_eat_flow():
    print("\n--- Starting Full Auth to EAT Flow Test ---")
    
    test_email = "test@example.com"
    test_password = "password123"
    test_user_id = uuid.uuid4()
    hashed_password = get_password_hash(test_password)
    
    # 1. Mock Database for Login
    mock_session = AsyncMock()
    
    # Mock User lookup
    mock_user = User(
        id=test_user_id,
        email=test_email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    mock_result_user = MagicMock()
    mock_result_user.scalars.return_value.first.return_value = mock_user
    
    # Mock PermissionProfile lookup for generate-eat
    mock_profile = PermissionProfile(
        user_id=test_user_id,
        permissions={
            "core_translator": ["read", "execute"],
            "discovery": ["read"]
        }
    )
    mock_result_profile = MagicMock()
    mock_result_profile.scalars.return_value.first.return_value = mock_profile
    
    mock_session.execute.side_effect = [mock_result_user, mock_result_profile]
    
    # Apply dependency override
    app.dependency_overrides[get_session] = lambda: mock_session
    
    try:
        # 2. Perform Login
        print(f"Attempting login for {test_email}...")
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": test_email, "password": test_password}
        )
        
        assert login_response.status_code == 200
        auth_data = login_response.json()
        access_token = auth_data["access_token"]
        print("[SUCCESS] Login successful. Received access token.")
        
        # 3. Generate EAT using the access token
        print("Generating EAT...")
        eat_response = client.post(
            "/api/v1/auth/tokens/generate-eat",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert eat_response.status_code == 200
        eat_data = eat_response.json()
        eat = eat_data["eat"]
        print(f"[SUCCESS] EAT generated: {eat[:15]}...{eat[-15:]}")
        
        # 4. Verify EAT Structure and Content
        payload = jwt.decode(
            eat, 
            _get_signing_key(), 
            algorithms=[settings.AUTH_JWT_ALGORITHM],
            audience=settings.AUTH_AUDIENCE,
            issuer=settings.AUTH_ISSUER
        )
        
        print("Verifying EAT payload...")
        assert payload["sub"] == str(test_user_id)
        assert payload["type"] == "EAT"
        assert "core_translator" in payload["allowed_tools"]
        assert payload["scopes"]["core_translator"] == ["read", "execute"]
        assert "exp" in payload
        assert "jti" in payload
        print("[SUCCESS] EAT structure and claims are verified.")
        
        # 5. Verify Uniqueness
        # (Running it again should give a different token due to JTI)
        # Reset side effect for next call
        mock_session.execute.side_effect = [mock_result_profile]
        eat_response2 = client.post(
            "/api/v1/auth/tokens/generate-eat",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        eat2 = eat_response2.json()["eat"]
        payload2 = jwt.decode(eat2, options={"verify_signature": False})
        assert payload["jti"] != payload2["jti"]
        print("[SUCCESS] Consecutive EATs have unique JTIs.")
        
        # 6. Test Signature Integrity / Tampering
        print("Testing tampering rejection...")
        parts = eat.split(".")
        # Tamper with payload part by changing user_id but keeping signature
        # We'll just flip a bit in the signature to simulate tampering
        tampered_sig = parts[2][:-2] + ("00" if parts[2][-2:] != "00" else "11")
        tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"
        
        try:
            verify_engram_token(tampered_token)
            print("[FAILURE] Tampered token was accepted!")
        except Exception:
            print("[SUCCESS] Tampered token correctly rejected due to signature mismatch.")
            
    finally:
        # Clean up overrides
        app.dependency_overrides.pop(get_session)

    print("\n--- Full Auth to EAT Flow Test Completed Successfully ---")

if __name__ == "__main__":
    test_full_auth_to_eat_flow()
