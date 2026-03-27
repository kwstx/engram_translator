from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from app.core.config import settings
import base64
import os

class CryptoService:
    _aes_gcm: AESGCM = None
    _salt: bytes = b"engram_default_salt" # In production, this should be configurable

    @classmethod
    def _get_aes_gcm(cls) -> AESGCM:
        if cls._aes_gcm is None:
            raw_key = settings.PROVIDER_CREDENTIALS_ENCRYPTION_KEY
            
            if not raw_key:
                if settings.ENVIRONMENT == "production":
                    raise ValueError("PROVIDER_CREDENTIALS_ENCRYPTION_KEY must be set in production")
                
                # Derive a key from AUTH_JWT_SECRET if available
                if settings.AUTH_JWT_SECRET:
                    # Use PBKDF2 to derive a strong 32-byte key for AES-256
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=cls._salt,
                        iterations=100000,
                        backend=default_backend()
                    )
                    key = kdf.derive(settings.AUTH_JWT_SECRET.encode())
                else:
                    # Fallback to a random key for the session (volatile!)
                    key = AESGCM.generate_key(bit_length=256)
            else:
                # If a key is provided, ensure it's 32 bytes or derive one from it
                if len(raw_key) == 44: # Likely a base64 encoded 32-byte key (Fernet-style)
                    try:
                        key = base64.urlsafe_b64decode(raw_key.encode())
                    except Exception:
                        key = raw_key.encode().ljust(32, b"0")[:32]
                else:
                    key = raw_key.encode().ljust(32, b"0")[:32]
            
            cls._aes_gcm = AESGCM(key)
        return cls._aes_gcm

    @classmethod
    def encrypt(cls, plain_text: str) -> str:
        if not plain_text:
            return ""
        aes_gcm = cls._get_aes_gcm()
        nonce = os.urandom(12)
        ciphertext = aes_gcm.encrypt(nonce, plain_text.encode(), None)
        # Store nonce + ciphertext
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()

    @classmethod
    def decrypt(cls, encrypted_text: str) -> str:
        if not encrypted_text:
            return ""
        aes_gcm = cls._get_aes_gcm()
        try:
            data = base64.urlsafe_b64decode(encrypted_text.encode())
            nonce = data[:12]
            ciphertext = data[12:]
            return aes_gcm.decrypt(nonce, ciphertext, None).decode()
        except Exception:
            # Handle decryption failure
            return ""

