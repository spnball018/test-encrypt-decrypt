from infrastructure.crypto_service import CryptoService
from infrastructure.repository import Repository
from domain.models import SubmitUserRequestModel

class SubmitCommandHandler:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.repository = Repository()

    def handle(self, command: SubmitUserRequestModel):
        # 1. Decrypt Transport Payload
        plaintext = self.crypto_service.decrypt_transport_payload(
            command.national_id,
            command.encrypted_key,
            command.iv
        )

        # 2. Encrypt for Storage (Column A)
        national_id_blob = self.crypto_service.encrypt_for_storage(plaintext)

        # 3. Hash for Index (Column B)
        national_id_index = self.crypto_service.hash_for_index(plaintext)

        # 4. Persist
        self.repository.save_user_profile(national_id_blob, national_id_index)
        
        return {"status": "success"}
