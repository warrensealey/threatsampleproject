"""
Encryption utilities for configuration secrets.

Only password fields are encrypted; all other configuration values remain in plain text.
"""
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet


DATA_DIR = Path(__file__).parent.parent / "data"
KEY_FILE = DATA_DIR / ".encryption_key"
ENV_KEY_NAME = "ENCRYPTION_KEY"
PREFIX = "encrypted:"


def _load_key_from_env() -> Optional[bytes]:
    """Load encryption key from environment variable, if set."""
    key = os.getenv(ENV_KEY_NAME)
    if not key:
        return None
    return key.encode("utf-8")


def _load_key_from_file() -> Optional[bytes]:
    """Load encryption key from key file, if present."""
    if not KEY_FILE.exists():
        return None
    data = KEY_FILE.read_bytes().strip()
    return data or None


def _write_key_file(key: bytes) -> None:
    """Write encryption key to key file with restrictive permissions."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_bytes(key)
    try:
        os.chmod(KEY_FILE, 0o600)
    except OSError:
        # Best-effort only; continue even if chmod is not supported
        pass


def get_encryption_key() -> bytes:
    """
    Get the symmetric encryption key, generating it if necessary.

    Precedence:
      1. ENCRYPTION_KEY environment variable
      2. data/.encryption_key file (auto-created if missing)
    """
    # 1) Environment variable takes precedence
    env_key = _load_key_from_env()
    if env_key:
        return env_key

    # 2) Key file, or create it if missing
    file_key = _load_key_from_file()
    if file_key:
        return file_key

    # Generate new key and persist to file
    new_key = Fernet.generate_key()
    _write_key_file(new_key)
    return new_key


def _get_fernet() -> Fernet:
    """Create a Fernet instance from the current key."""
    key = get_encryption_key()
    return Fernet(key)


def is_encrypted(value) -> bool:
    """Return True if the given value looks like an encrypted string."""
    return isinstance(value, str) and value.startswith(PREFIX)


def encrypt_value(value: Optional[str]) -> Optional[str]:
    """
    Encrypt a string value and return it with the encrypted: prefix.

    If value is falsy (None/empty), it is returned unchanged.
    """
    if not value:
        return value
    if is_encrypted(value):
        return value

    f = _get_fernet()
    token = f.encrypt(str(value).encode("utf-8"))
    return f"{PREFIX}{token.decode('utf-8')}"


def decrypt_value(value: Optional[str]) -> Optional[str]:
    """
    Decrypt a value if it is prefixed as encrypted; otherwise return as-is.
    """
    if not is_encrypted(value):
        return value

    token = value[len(PREFIX) :].encode("utf-8")
    f = _get_fernet()
    plain = f.decrypt(token)
    return plain.decode("utf-8")



