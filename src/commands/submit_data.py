from infrastructure.crypto_service import CryptoService
from infrastructure.repository import Repository
from domain.models import SubmitUserRequestModel
from marshmallow import Schema, fields, validate, ValidationError

class NationalIdSchema(Schema):
    national_id = fields.String(required=True, validate=[
        validate.Length(equal=13, error="National ID must be exactly 13 digits"),
        validate.Regexp(r'^\d+$', error="National ID must contain only digits")
    ])

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

        # Validation: Use Marshmallow Schema
        try:
            NationalIdSchema().load({"national_id": plaintext})
        except ValidationError as err:
            # Flatten errors for simpler response or re-raise
            raise ValueError(f"Invalid National ID: {err.messages}")

        # 2. Encrypt for Storage (Column A)
        national_id_blob = self.crypto_service.encrypt_for_storage(plaintext)

        # 3. Hash for Index (Column B)
        national_id_index = self.crypto_service.hash_for_index(plaintext)

        # 4. Persist
        self.repository.save_user_profile(national_id_blob, national_id_index)
        
        return {"status": "success"}
