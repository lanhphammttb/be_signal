from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
import aiofiles
import hashlib
import asyncio
import os
from dotenv import load_dotenv
from crypto_utils import hash_file, sign_file
from schemas import RegisterMetadata, RegisterResponse
import json
from web3 import Web3

# Config
UPLOAD_FOLDER = "storage"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
load_dotenv()
# MUMBAI_RPC_URL = os.getenv("MUMBAI_RPC_URL")
# PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")
# w3 = Web3(Web3.HTTPProvider(MUMBAI_RPC_URL))
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


# DB model
class CopyrightRecord(Base):
    __tablename__ = "copyright_records"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    blockchain_tx_hash = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class RegisterResponse(BaseModel):
    id: int
    title: str
    description: str
    file_hash: str
    signature: str
    file_path: str
    blockchain_tx_hash: str | None
    created_at: datetime

    class Config:
        from_attributes = True

# IPFS và Blockchain giả lập
async def upload_to_ipfs(filepath: str) -> str:
    async with aiofiles.open(filepath, "rb") as f:
        content = await f.read()
    cid = hashlib.sha256(content).hexdigest()
    await asyncio.sleep(0.1)
    return cid

# giả
async def write_to_blockchain(metadata: dict) -> str:
    import json
    await asyncio.sleep(0.2)
    return hashlib.sha256(json.dumps(metadata).encode()).hexdigest()

# thật
# async def write_to_blockchain(metadata: dict) -> str:
#     data = json.dumps(metadata).encode("utf-8").hex()
#     nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)

#     tx = {
#         "nonce": nonce,
#         "to": PUBLIC_ADDRESS,
#         "value": 0,
#         "gas": 300000,
#         "gasPrice": w3.to_wei("10", "gwei"),
#         "data": "0x" + data,
#         "chainId": 137,
#     }

#     signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
#     return tx_hash.hex()

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tạo bảng tự động khi startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/register", response_model=RegisterResponse)
async def register(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        file_hash = hashlib.sha256(content).hexdigest()
        signature_bytes = sign_file(file_path, "keys/private.pem")
        signature_hex = signature_bytes.hex()

        # ipfs_cid = await upload_to_ipfs(file_path)

        metadata = {
            "title": title,
            "description": description,
            "file_hash": file_hash,
            "signature": signature_hex,
            "file_path": file_path,
            "timestamp": datetime.utcnow().isoformat()
        }
        blockchain_tx_hash = await write_to_blockchain(metadata)

        record = CopyrightRecord(
            title=title,
            description=description,
            file_hash=file_hash,
            signature=signature_hex,
            file_path=file_path,
            blockchain_tx_hash=blockchain_tx_hash
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)

        return RegisterResponse.from_orm(record)
    except Exception as e:
        print(f"Error in /register: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")