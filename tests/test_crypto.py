"""Tests for env-vault crypto layer."""

import pytest
from env_vault.crypto import VaultCrypto


def test_encrypt_decrypt_roundtrip():
    crypto = VaultCrypto("my-test-password-123")
    plaintext = b"DATABASE_URL=postgres://user:pass@localhost/db\nSECRET_KEY=abc123"
    encrypted = crypto.encrypt(plaintext)
    assert encrypted != plaintext
    assert len(encrypted) > len(plaintext)
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == plaintext


def test_magic_header():
    crypto = VaultCrypto("pass")
    blob = crypto.encrypt(b"test")
    assert blob[:4] == b"ENVV"


def test_wrong_password_raises():
    c1 = VaultCrypto("correct-password")
    c2 = VaultCrypto("wrong-password")
    blob = c1.encrypt(b"secret data")
    with pytest.raises(Exception):
        c2.decrypt(blob)


def test_invalid_blob_raises():
    crypto = VaultCrypto("pass")
    with pytest.raises(ValueError, match="Not a valid env-vault file"):
        crypto.decrypt(b"INVALID_MAGIC_BYTES_HERE")


def test_different_salts_each_time():
    crypto = VaultCrypto("same-password")
    blob1 = crypto.encrypt(b"data")
    blob2 = crypto.encrypt(b"data")
    # Different salt → different ciphertext
    assert blob1 != blob2
    # But both decrypt correctly
    assert crypto.decrypt(blob1) == b"data"
    assert crypto.decrypt(blob2) == b"data"


def test_empty_plaintext():
    crypto = VaultCrypto("pass")
    blob = crypto.encrypt(b"")
    assert crypto.decrypt(blob) == b""


def test_large_plaintext():
    crypto = VaultCrypto("pass")
    big = b"KEY=VALUE\n" * 10_000
    blob = crypto.encrypt(big)
    assert crypto.decrypt(blob) == big
