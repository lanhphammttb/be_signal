from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.crypto import sign_file
from app.models import CopyrightRecord
from app.schemas import RegisterResponse
from app.ipfs_utils import upload_to_ipfs
from app.utils.blockchain import write_to_blockchain
from app.database import get_session
import hashlib, aiofiles, os, datetime
from datetime import datetime
# Config
UPLOAD_FOLDER = "storage"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter()

@router.post("/", response_model=RegisterResponse)
async def register(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
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
            blockchain_tx_hash=blockchain_tx_hash,
            owner_address="0x0000000000000000000000000000000000000000"
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)

        return RegisterResponse.from_orm(record)
    except Exception as e:
        print("ERROR /register:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
