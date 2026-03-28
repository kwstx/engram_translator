import sys
from unittest.mock import MagicMock
sys.modules["pyswip"] = MagicMock()

try:
    from app.core.security import create_engram_access_token
    print("Security import success")
    from app.services.credentials import CredentialService
    print("Credentials import success")
    from app.db.models import ProviderCredential
    print("Models import success")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
