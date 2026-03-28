import os
import json
import time
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet, InvalidToken

CONFIG_DIR = os.path.expanduser("~/.engram")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.enc")
KEY_FILE = os.path.join(CONFIG_DIR, "key")
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

def _ensure_key() -> bytes:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    try:
        os.chmod(KEY_FILE, 0o600)
    except OSError:
        pass
    return key

def _get_fernet() -> Fernet:
    return Fernet(_ensure_key())

def _encrypt_config(config: Dict[str, Any]) -> str:
    payload = json.dumps(config).encode("utf-8")
    return _get_fernet().encrypt(payload).decode("utf-8")

def _decrypt_config(token: str) -> Dict[str, Any]:
    payload = _get_fernet().decrypt(token.encode("utf-8"))
    return json.loads(payload.decode("utf-8"))

def _default_config() -> Dict[str, Any]:
    return {
        "base_url": DEFAULT_BASE_URL, 
        "token": None, 
        "eat": None, 
        "email": None,
        "vault": {}
    }

def _normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    base = _default_config()
    base.update(config or {})
    return base

def load_vault_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return _normalize_config(_decrypt_config(f.read().strip()))
        except (InvalidToken, json.JSONDecodeError, OSError):
            return _default_config()
    return _default_config()

def save_vault_config(config: Dict[str, Any]) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(_encrypt_config(config))

class VaultService:
    @staticmethod
    def get_credential(base_url: str, email: str, provider_id: str) -> Optional[Dict[str, Any]]:
        config = load_vault_config()
        vault_key = f"{base_url}|{email}"
        return config.get("vault", {}).get(vault_key, {}).get(provider_id)

    @staticmethod
    def store_credential(base_url: str, email: str, provider_id: str, credential_data: Dict[str, Any]) -> None:
        config = load_vault_config()
        if "vault" not in config:
            config["vault"] = {}
        vault_key = f"{base_url}|{email}"
        if vault_key not in config["vault"]:
            config["vault"][vault_key] = {}
        
        # Add timestamp
        credential_data["last_synced"] = time.time()
        config["vault"][vault_key][provider_id] = credential_data
        save_vault_config(config)

    @staticmethod
    def list_credentials(base_url: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        config = load_vault_config()
        vault = config.get("vault", {})
        if base_url and email:
            vault_key = f"{base_url}|{email}"
            return vault.get(vault_key, {})
        return vault

    @staticmethod
    def clear_vault(base_url: Optional[str] = None, email: Optional[str] = None, provider_id: Optional[str] = None) -> None:
        config = load_vault_config()
        if not base_url or not email:
            config["vault"] = {}
        else:
            vault_key = f"{base_url}|{email}"
            if vault_key in config.get("vault", {}):
                if provider_id:
                    if provider_id in config["vault"][vault_key]:
                        del config["vault"][vault_key][provider_id]
                else:
                    del config["vault"][vault_key]
        save_vault_config(config)
