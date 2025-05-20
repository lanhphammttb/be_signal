from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import CopyrightRecord
from app.schemas import PurchaseRequest
from app.utils.blockchain import record_license_transaction_mock  # dùng mock blockchain

router = APIRouter()

@router.post("/{record_id}/purchase")
async def purchase_license(
    record_id: int,
    payload: PurchaseRequest,
    session: AsyncSession = Depends(get_session)
):
    buyer_address = payload.buyer_address
    # Lấy bản ghi từ DB
    result = await session.execute(
        select(CopyrightRecord).where(CopyrightRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản quyền")
    if not record.approved or not record.blockchain_tx_hash:
        raise HTTPException(status_code=400, detail="Bản quyền chưa được xác minh trên blockchain")

    # Gửi giao dịch lên blockchain (mock hoặc thật)
    try:
        tx_hash = await record_license_transaction_mock({
            "record_id": record.id,
            "title": record.title,
            "file_hash": record.file_hash,
            "buyer_address": buyer_address,
            "owner_address": record.owner_address
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi ghi blockchain: {str(e)}")

    # Có thể ghi thêm log vào bảng khác nếu cần (ví dụ bảng `LicenseTransaction`)
    return {
        "message": "Giao dịch mua quyền sử dụng đã ghi thành công",
        "tx_hash": tx_hash
    }
