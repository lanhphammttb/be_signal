from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_session
from app.models import CopyrightRecord
from app.schemas import RegisterResponse

router = APIRouter()

@router.get("/{id}", response_model=RegisterResponse)
async def get_record(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(CopyrightRecord).where(CopyrightRecord.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return RegisterResponse.from_orm(record)
