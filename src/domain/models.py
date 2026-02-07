from pydantic import BaseModel
from typing import Optional

class SecureDataModel(BaseModel):
    id: Optional[int]
    encrypted_blob: str
    search_hash: str
    created_at: Optional[str]

class SubmitRequest(BaseModel):
    encrypted_data: str
    encrypted_key: str
    iv: str
