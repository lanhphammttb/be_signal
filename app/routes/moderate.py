from fastapi import APIRouter, HTTPException, Depends
from requests import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import  get_session
from app.models import CopyrightRecord
from app.schemas import RegisterResponse
from app.utils.blockchain import record_on_blockchain_mock

router = APIRouter()

@router.post("/{record_id}/approve")
async def approve_record(record_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(CopyrightRecord).where(CopyrightRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    blockchain_data = {
        "title": record.title,
        "description": record.description,
        "file_hash": record.file_hash,
        "owner": record.owner_address or "0x0000000000000000000000000000000000000000"
    }

    try:
        tx_hash = await record_on_blockchain_mock(blockchain_data)  # async mock call
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ghi blockchain thất bại: {str(e)}")


    record.approved = True
    record.blockchain_tx_hash = tx_hash
    await session.commit()
    return {"message": "Approved"}

@router.get("/list", response_model=list[RegisterResponse])
async def list_pending_copyrights(db: AsyncSession = Depends(get_session)):
    stmt = select(CopyrightRecord).where(CopyrightRecord.approved == False)
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [RegisterResponse.from_orm(record) for record in records]