import os
import base64
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

from .storage_cipher_adapters import load_key_from_env, StorageCipherAdapter, V1StorageCipher

class CryptoService:
    def __init__(self):
        # Load Server Private Key (for Transport Decryption)
        self.private_key = self._load_private_key()
        
        # Load HMAC Key (for Indexing - Column B)
        # Using a separate key or deriving it is best practice.
        self.hmac_key = load_key_from_env("HMAC_KEY")

        # Initialize Storage Adapters
        self.storage_adapters = [
            V1StorageCipher()
        ]
        # Default to the last one (assumed latest) or explicit V1
        self.default_storage_adapter = self.storage_adapters[0]

    def _load_private_key(self):
        # In a real app, load from file or secure vault. 
        # For this demo, we expect a path or raw PEM in env.
        # Minimal implementation: Generate if missing (for dev ease) or fail.
        # Let's try to load from a file path specified in env, or fall back to a default location.
        key_path = os.getenv("PRIVATE_KEY_PATH", "private_key.pem")
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
        
        # Fallback to certs/private_key.pem (common dev pattern)
        fallback_path = "certs/private_key.pem"
        if os.path.exists(fallback_path):
            with open(fallback_path, "rb") as f:
                return serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )

        # Check env var direct content
        key_content = os.getenv("PRIVATE_KEY_CONTENT")
        if key_content:
             return serialization.load_pem_private_key(
                key_content.encode(),
                password=None,
                backend=default_backend()
            )
        raise ValueError(f"Server Private Key not found (checked {key_path}, {fallback_path} and PRIVATE_KEY_CONTENT)")

    def get_public_key_pem(self) -> str:
        """
        Derives the public key from the private key and returns it in PEM format.
        """
        public_key = self.private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def decrypt_transport_payload(self, encrypted_data_b64: str, encrypted_key_b64: str, iv_b64: str) -> str:
        """
        Decrypts the hybrid encryption payload from Frontend.
        """
        logger.info(f"Decrypting transport payload. Data len: {len(encrypted_data_b64)}, Key len: {len(encrypted_key_b64)}")
        encrypted_key = base64.b64decode(encrypted_key_b64)
        encrypted_data = base64.b64decode(encrypted_data_b64)
        iv = base64.b64decode(iv_b64)

        # 1. Decrypt Symmetric Key using Private Key
        symmetric_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 2. Decrypt Data using Symmetric Key (AES-GCM)
        aesgcm = AESGCM(symmetric_key)
        # WebCrypto encrypts tag at end of ciphertext usually. 
        # Python cryptography AESGCM expects ciphertext + tag combined as data.
        # This matches the standard GCM construction.
        plaintext_bytes = aesgcm.decrypt(iv, encrypted_data, None)
        
        logger.info("Transport payload decrypted successfully")
        return plaintext_bytes.decode('utf-8')

    def encrypt_for_storage(self, plaintext: str) -> str:
        """
        Column A: Randomized Encryption using default adapter.
        """
        logger.info("Encrypting for storage...")
        blob = self.default_storage_adapter.encrypt(plaintext.encode())
        return base64.b64encode(blob).decode('utf-8')

    def decrypt_from_storage(self, blob_b64: str) -> str:
        logger.info("Decrypting from storage...")
        blob = base64.b64decode(blob_b64)
        
        for adapter in self.storage_adapters:
            if blob.startswith(adapter.version_prefix):
                return adapter.decrypt(blob).decode('utf-8')
        
        raise ValueError("Unknown storage encryption version")

    def hash_for_index(self, plaintext: str) -> str:
        """
        Column B: Deterministic Hash (HMAC-SHA256).
        """
        logger.info("Hashing for index...")
        h = HMAC(self.hmac_key, hashes.SHA256(), backend=default_backend())
        h.update(plaintext.encode())
        return base64.b64encode(h.finalize()).decode('utf-8')
