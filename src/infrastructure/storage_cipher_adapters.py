import os
import base64
from abc import ABC, abstractmethod
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

def load_key_from_env(var_name: str, default=None):
    val = os.getenv(var_name)
    if not val:
        if default: return default
        raise ValueError(f"Missing required environment variable: {var_name}")
    # Assuming key is hex or base64? Let's assume URL-safe Base64 or just 32 bytes hex.
    # For simplicity in this demo, let's treat it as a string that we hash to get bytes if it's not proper length.
    # Better: use a proper KDF.
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(val.encode())
    return digest.finalize()

class StorageCipherAdapter(ABC):
    @property
    @abstractmethod
    def version_prefix(self) -> bytes:
        pass

    @abstractmethod
    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypts plaintext and returns blob with version prefix"""
        pass

    @abstractmethod
    def decrypt(self, blob: bytes) -> bytes:
        """Decrypts full blob (including prefix)"""
        pass

class V1StorageCipher(StorageCipherAdapter):
    def __init__(self):
        self.key = load_key_from_env("DEK_KEY")
        self.prefix = b"v1:"

    @property
    def version_prefix(self) -> bytes:
        return self.prefix

    def encrypt(self, plaintext: bytes) -> bytes:
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return self.prefix + nonce + ciphertext

    def decrypt(self, blob: bytes) -> bytes:
        if not blob.startswith(self.prefix):
            raise ValueError("Invalid version prefix for V1 adapter")
        
        payload = blob[len(self.prefix):]
        if len(payload) < 12: # At least nonce needs to be there
             raise ValueError("Invalid V1 payload length")
             
        nonce = payload[:12]
        ciphertext = payload[12:]
        
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, None)
