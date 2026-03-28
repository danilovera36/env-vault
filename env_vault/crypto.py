"""AES-256 encryption/decryption for env-vault using Fernet (cryptography library)."""

import os
import base64
import hashlib
from cryptography.fernet import Fernet


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from a password using PBKDF2-HMAC-SHA256."""
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=600_000,
        dklen=32,
    )
    return base64.urlsafe_b64encode(key)


class VaultCrypto:
    """
    Symmetric encryption wrapper using Fernet (AES-128-CBC + HMAC-SHA256).

    Format of the encrypted blob:
      [4 bytes magic] [16 bytes salt] [Fernet token...]
    """

    MAGIC = b"ENVV"
    SALT_SIZE = 16

    def __init__(self, key_or_password: str):
        self._raw = key_or_password

    def _fernet(self, salt: bytes) -> Fernet:
        key = _derive_key(self._raw, salt)
        return Fernet(key)

    def encrypt(self, plaintext: bytes) -> bytes:
        salt = os.urandom(self.SALT_SIZE)
        f = self._fernet(salt)
        token = f.encrypt(plaintext)
        return self.MAGIC + salt + token

    def decrypt(self, blob: bytes) -> bytes:
        if not blob.startswith(self.MAGIC):
            raise ValueError("Not a valid env-vault file (wrong magic bytes).")
        salt = blob[len(self.MAGIC):len(self.MAGIC) + self.SALT_SIZE]
        token = blob[len(self.MAGIC) + self.SALT_SIZE:]
        f = self._fernet(salt)
        return f.decrypt(token)
