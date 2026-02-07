import psycopg2
from infrastructure.crypto_service import CryptoService
import os

class Repository:
    def __init__(self):
        self.conn_str = os.getenv("DATABASE_URL")
    
    def get_connection(self):
        return psycopg2.connect(self.conn_str)

    def save_secure_data(self, encrypted_blob: str, search_hash: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Create table if not exists (demo only, use migration tool in prod)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS secure_data (
                        id SERIAL PRIMARY KEY,
                        encrypted_blob TEXT NOT NULL,
                        search_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute(
                    "INSERT INTO secure_data (encrypted_blob, search_hash) VALUES (%s, %s)",
                    (encrypted_blob, search_hash)
                )
            conn.commit()
        finally:
            conn.close()

    def find_by_hash(self, search_hash: str):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, encrypted_blob FROM secure_data WHERE search_hash = %s",
                    (search_hash,)
                )
                return cur.fetchall()
        finally:
            conn.close()
