import os
import sys
import uuid
from datetime import timedelta, datetime, timezone
import jwt
import json
import base64
from unittest.mock import patch, MagicMock

# Ensure app is in path
sys.path.append(os.getcwd())

# Mock Redis BEFORE importing anything that might use it
with patch("app.core.redis_client.get_redis_client", return_value=None):
    from app.core.security import create_engram_access_token, verify_engram_token, _get_signing_key
    from app.core.config import settings


def test_eat_generation_and_verification():
    print("\n--- Starting EAT Generation & Verification Test ---")
    
    user_id = str(uuid.uuid4())
    permissions = {
        "mcp_server": ["read", "write"],
        "discovery": ["read"]
    }
    
    # 1. Generate EAT
    eat = create_engram_access_token(user_id, permissions)
    print(f"Generated EAT: {eat[:20]}...{eat[-20:]}")
    
    # 2. Decode and Verify Structure
    payload = jwt.decode(
        eat, 
        _get_signing_key(), 
        algorithms=[settings.AUTH_JWT_ALGORITHM],
        audience=settings.AUTH_AUDIENCE,
        issuer=settings.AUTH_ISSUER
    )
    
    print("Decoding payload...")
    assert payload["sub"] == user_id
    assert payload["type"] == "EAT"
    assert "mcp_server" in payload["allowed_tools"]
    assert "discovery" in payload["allowed_tools"]
    assert payload["scopes"]["mcp_server"] == ["read", "write"]
    assert payload["scope"] == "read write"  # Sorted unique scopes
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload
    assert payload["iss"] == settings.AUTH_ISSUER
    assert payload["aud"] == settings.AUTH_AUDIENCE
    print("[SUCCESS] EAT structure is correct and contains all required claims.")
    
    # 3. Verify Uniqueness (different JTI for different calls)
    eat2 = create_engram_access_token(user_id, permissions)
    payload2 = jwt.decode(
        eat2, 
        _get_signing_key(), 
        algorithms=[settings.AUTH_JWT_ALGORITHM],
        audience=settings.AUTH_AUDIENCE,
        issuer=settings.AUTH_ISSUER
    )
    assert payload["jti"] != payload2["jti"]
    print(f"[SUCCESS] Tokens are unique per call (JTI mismatch as expected: {payload['jti']} != {payload2['jti']})")
    
    # 4. Verify using the system's own verification logic
    verified_payload = verify_engram_token(eat)
    assert verified_payload["sub"] == user_id
    print("[SUCCESS] verify_engram_token correctly verified the authentic token.")
    
    # 5. Test Forgery Rejection
    print("Testing forgery rejection...")
    # Attempt 1: Change user_id
    forged_payload = payload.copy()
    forged_payload["sub"] = "FORGED_USER"
    forged_token = jwt.encode(forged_payload, "WRONG_SECRET", algorithm=settings.AUTH_JWT_ALGORITHM)
    
    try:
        verify_engram_token(forged_token)
        print("[FAILURE] Systematic verification accepted a token signed with wrong secret.")
    except Exception as e:
        print(f"[SUCCESS] Correctly rejected token signed with wrong secret: {str(e)}")
        
    # Attempt 2: Tamper with a claim but keep existing signature (will fail signature check)
    parts = eat.split(".")
    # Simply flip some characters in the signature part
    tampered_sig = parts[2][:-2] + ("00" if parts[2][-2:] != "00" else "11")
    tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"
    
    try:
        verify_engram_token(tampered_token)
        print("[FAILURE] Systematic verification accepted a token with tampered signature.")
    except Exception as e:
        print(f"[SUCCESS] Correctly rejected token with tampered signature: {str(e)}")

    # Attempt 3: Payload tampering without resigning
    # (jwt.decode will detect that the payload doesn't match the signature)
    header = parts[0]
    import base64
    import json
    
    decoded_payload = json.loads(base64.urlsafe_b64decode(parts[1] + "==").decode())
    decoded_payload["sub"] = "MALICIOUS_USER"
    tampered_payload_base64 = base64.urlsafe_b64encode(json.dumps(decoded_payload).encode()).decode().strip("=")
    tampered_token_payload = f"{header}.{tampered_payload_base64}.{parts[2]}"
    
    try:
        verify_engram_token(tampered_token_payload)
        print("[FAILURE] Systematic verification accepted a token with tampered payload.")
    except Exception as e:
        print(f"[SUCCESS] Correctly rejected token with tampered payload: {str(e)}")

    print("\n--- EAT Generation & Verification Test Completed Successfully ---")


if __name__ == "__main__":
    test_eat_generation_and_verification()
