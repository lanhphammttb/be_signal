from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RegisterMetadata(BaseModel):
    title: str
    description: str

class RegisterResponse(BaseModel):
    id: int
    title: str
    description: str
    file_hash: str
    signature: str
    blockchain_tx_hash: Optional[str]
    created_at: datetime
    approved: bool
    owner_address: Optional[str]

    class Config:
        from_attributes = True
    
class PurchaseRequest(BaseModel):
    buyer_address: str