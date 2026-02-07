from infrastructure.crypto_service import CryptoService
from infrastructure.repository import Repository
from domain.models import SubmitRequest

class SubmitCommandHandler:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.repository = Repository()

    def handle(self, command: SubmitRequest):
        # 1. Decrypt Transport Payload
        plaintext = self.crypto_service.decrypt_transport_payload(
            command.encrypted_data,
            command.encrypted_key,
            command.iv
        )

        # 2. Encrypt for Storage (Column A)
        encrypted_blob = self.crypto_service.encrypt_for_storage(plaintext)

        # 3. Hash for Index (Column B)
        search_hash = self.crypto_service.hash_for_index(plaintext)

        # 4. Persist
        self.repository.save_secure_data(encrypted_blob, search_hash)
        
        return {"status": "success"}
