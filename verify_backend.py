import sys
import os
import json
import base64

# Add 'src' directory relative to this script location
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'src'))

from infrastructure.crypto_service import CryptoService

def test_decryption():
    print("Loading payload.json...")
    try:
        with open('payload.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("payload.json not found. Run frontend test first.")
        return

    # Setup Environment
    os.environ['PRIVATE_KEY_PATH'] = 'certs/private_key.pem'
    os.environ['DEK_KEY'] = 'MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=' # 32 bytes base64 mock
    os.environ['HMAC_KEY'] = os.environ['DEK_KEY']

    print("Initializing CryptoService...")
    service = CryptoService()

    print("Decrypting Transport Payload...")
    plaintext = service.decrypt_transport_payload(
        data['national_id'],
        data['encrypted_key'],
        data['iv']
    )
    print(f"Decrypted Data: {plaintext}")
    
    assert plaintext == "1234567890123"
    print("SUCCESS: Decryption matches original data.")

    print("Testing Storage Encryption...")
    encrypted_blob = service.encrypt_for_storage(plaintext)
    print(f"Encrypted Blob: {encrypted_blob}")
    
    decrypted_storage = service.decrypt_from_storage(encrypted_blob)
    assert decrypted_storage == plaintext
    print("SUCCESS: Storage Encryption/Decryption verified.")

    print("Testing Index Hash...")
    idx_hash = service.hash_for_index(plaintext)
    print(f"Index Hash: {idx_hash}")

if __name__ == '__main__':
    test_decryption()
