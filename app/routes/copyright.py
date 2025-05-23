from app.core.auth import get_current_user, get_current_user_from_cookie
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils.crypto import sign_file
from app.models import CopyrightRecord
from app.schemas import RegisterResponse, User
from app.utils.blockchain import write_to_blockchain
from app.database import get_session
import hashlib, aiofiles, os
from datetime import datetime

UPLOAD_FOLDER = "storage"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter()

class DuplicateCopyrightException(HTTPException):
    def __init__(self, detail="Nội dung này đã được đăng ký bản quyền trước đó."):
        super().__init__(status_code=400, detail=detail)

@router.post("/register", response_model=RegisterResponse)
async def register(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        content = await file.read()

        # Lưu file async
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(content)

        file_hash = hashlib.sha256(content).hexdigest()

        # Kiểm tra trùng hash
        result = await session.execute(
            select(CopyrightRecord).where(CopyrightRecord.file_hash == file_hash)
        )
        existing_record = result.scalars().first()
        if existing_record:
            raise DuplicateCopyrightException()

        signature_bytes = sign_file(file_path, "keys/private.pem")
        signature_hex = signature_bytes.hex()

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
            owner_address="0x0000000000000000000000000000000000000000",
            owner_id=current_user.id,
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)

        return RegisterResponse.from_orm(record)

    except DuplicateCopyrightException as e:
        # Trả lỗi 400 rõ ràng khi trùng bản quyền
        raise e

    except Exception as e:
        print("ERROR /register:", e)
        # Có thể bổ sung log chi tiết với traceback nếu cần
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{id}", response_model=RegisterResponse)
async def get_record(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(CopyrightRecord).where(CopyrightRecord.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return RegisterResponse.from_orm(record)
