import pytest
import os
import base64
from unittest.mock import patch, MagicMock
from infrastructure.crypto_service import CryptoService

@pytest.fixture
def mock_env_keys(monkeypatch):
    # Mock DEK_KEY and Private Key Path
    monkeypatch.setenv("DEK_KEY", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=") # 32 bytes base64
    monkeypatch.setenv("HMAC_KEY", "NmE0OWM1YjYyMDNmNDYyZDFjMmY0MjAxMGQwYzNiYjU=") # Mock HMAC Key
    monkeypatch.setenv("PRIVATE_KEY_CONTENT", "") # Clear content to force file/mock usage
    pass

def test_load_key_from_env_success(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "c29tZXNlY3JldA==") # "somesecret"
    # Test the standalone function
    from infrastructure.storage_cipher_adapters import load_key_from_env
    key = load_key_from_env("TEST_KEY")
    assert key is not None

def test_load_key_from_env_missing():
    from infrastructure.storage_cipher_adapters import load_key_from_env
    with pytest.raises(ValueError):
        load_key_from_env("NON_EXISTENT_KEY")

def test_encrypt_decrypt_storage_loop(mock_env_keys, monkeypatch):
    # Setup service with mocked keys
    with patch.object(CryptoService, '_load_private_key') as mock_load_pk:
        mock_load_pk.return_value = MagicMock() # We don't need PK for storage encrypt
        
        # Ensure DEK_KEY is loaded
        monkeypatch.setenv("DEK_KEY", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=")
        service = CryptoService()
        
        original_text = "Sensitive Data 123"
        encrypted_blob = service.encrypt_for_storage(original_text)
        
        assert encrypted_blob != original_text
        
        decrypted_text = service.decrypt_from_storage(encrypted_blob)
        assert decrypted_text == original_text

def test_hash_for_index_deterministic(mock_env_keys, monkeypatch):
    with patch.object(CryptoService, '_load_private_key'):
        monkeypatch.setenv("DEK_KEY", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=")
        service = CryptoService()
        
        input_text = "NationalID123"
        hash1 = service.hash_for_index(input_text)
        hash2 = service.hash_for_index(input_text)
        
        assert hash1 == hash2
        assert hash1 != input_text
