from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models import CopyrightRecord
from app.schemas import  RegisterResponse

router = APIRouter()

@router.get("", response_model=list[RegisterResponse])
async def list_public_records(db: AsyncSession = Depends(get_session)):
    stmt = select(CopyrightRecord).where(CopyrightRecord.blockchain_tx_hash.is_not(None))
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [RegisterResponse.from_orm(record) for record in records]

@router.get("/{id}", response_model=RegisterResponse)
async def get_record(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(CopyrightRecord).where(CopyrightRecord.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return RegisterResponse.from_orm(record)
