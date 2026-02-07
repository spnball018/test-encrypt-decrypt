from infrastructure.crypto_service import CryptoService
from infrastructure.repository import Repository
import logging

logger = logging.getLogger(__name__)

class SearchQueryHandler:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.repository = Repository()

    def handle(self, national_id: str):
        logger.info(f"Handling search for national_id: {national_id}")
        # 1. Compute Hash for Index
        national_id_index = self.crypto_service.hash_for_index(national_id)

        # 2. Query Database
        results = self.repository.find_by_hash(national_id_index)

        # 3. Decrypt Results (Optional - depends on requirement)
        # Assuming we want to verify we can recover the data
        decrypted_results = []
        for row in results:
            id, blob = row
            plaintext = self.crypto_service.decrypt_from_storage(blob)
            decrypted_results.append({
                "id": id,
                "data": plaintext
            })
            
        logger.info(f"Search returned {len(decrypted_results)} decrypted results")
        return decrypted_results
