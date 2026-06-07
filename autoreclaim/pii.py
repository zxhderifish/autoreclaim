from __future__ import annotations

import json
from pathlib import Path

import keyring
from cryptography.fernet import Fernet

KEYCHAIN_SERVICE = "autoreclaim"
KEYCHAIN_USER = "pii-fernet-key"


class PiiKeyMissing(Exception):
    """Raised when the Keychain key is absent but ciphertext exists."""


def get_or_create_key() -> bytes:
    existing = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_USER)
    if existing:
        return existing.encode()
    key = Fernet.generate_key()
    keyring.set_password(KEYCHAIN_SERVICE, KEYCHAIN_USER, key.decode())
    return key


def _require_key() -> bytes:
    existing = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_USER)
    if not existing:
        raise PiiKeyMissing("No AutoReclaim PII key in Keychain — run onboarding/setup_pii.py")
    return existing.encode()


def save_pii(path, data: dict) -> None:
    f = Fernet(get_or_create_key())
    token = f.encrypt(json.dumps(data).encode())
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(token)


def load_pii(path) -> dict:
    f = Fernet(_require_key())
    token = Path(path).read_bytes()
    return json.loads(f.decrypt(token).decode())
