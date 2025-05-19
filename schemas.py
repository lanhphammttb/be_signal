from pydantic import BaseModel

class RegisterMetadata(BaseModel):
    title: str
    description: str

class RegisterResponse(BaseModel):
    id: int
    title: str
    description: str
    file_hash: str
    signature: str
    ipfs_cid: str
    blockchain_tx_hash: str
    created_at: str
