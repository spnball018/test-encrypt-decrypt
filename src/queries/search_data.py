from infrastructure.crypto_service import CryptoService
from infrastructure.repository import Repository

class SearchQueryHandler:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.repository = Repository()

    def handle(self, national_id: str):
        # 1. Compute Hash for Index
        search_hash = self.crypto_service.hash_for_index(national_id)

        # 2. Query Database
        results = self.repository.find_by_hash(search_hash)

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
            
        return decrypted_results
