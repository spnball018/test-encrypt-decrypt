from pydantic import BaseModel
from typing import Optional

class UserProfileModel(BaseModel):
    id: Optional[int]
    national_id_blob: str
    national_id_index: str
    created_at: Optional[str]

class SubmitUserRequestModel(BaseModel):
    national_id: str
    encrypted_key: str
    iv: str
