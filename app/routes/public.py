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


