import psycopg2
from infrastructure.crypto_service import CryptoService
import os
import logging

logger = logging.getLogger(__name__)

class Repository:
    def __init__(self):
        self.conn_str = os.getenv("DATABASE_URL")
    
    def get_connection(self):
        return psycopg2.connect(self.conn_str)

    def save_user_profile(self, national_id_blob: str, national_id_index: str):
        logger.info(f"Saving user profile. Index hash prefix: {national_id_index[:10]}...")
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Create table if not exists (demo only, use migration tool in prod)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id SERIAL PRIMARY KEY,
                        national_id_blob VARCHAR(255) NOT NULL,
                        national_id_index VARCHAR(64) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute(
                    "INSERT INTO user_profiles (national_id_blob, national_id_index) VALUES (%s, %s)",
                    (national_id_blob, national_id_index)
                )
            conn.commit()
            logger.info("User profile saved successfully")
        finally:
            conn.close()

    def find_by_hash(self, national_id_index: str):
        logger.info(f"Finding user profile by hash. Prefix: {national_id_index[:10]}...")
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, national_id_blob FROM user_profiles WHERE national_id_index = %s",
                    (national_id_index,)
                )
                results = cur.fetchall()
                logger.info(f"Found {len(results)} profiles")
                return results
        finally:
            conn.close()
