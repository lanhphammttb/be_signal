from app.core.constaint import ALGORITHM, SECRET_KEY
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from app.models import User
from app.database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # token URL cần khớp

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Không thể xác thực token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")

    return user

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới được phép truy cập"
        )
    return current_user

async def get_current_user_from_cookie(
    token: str = Cookie(None, alias="access_token"),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chưa đăng nhập")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")

    return user

async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    return user
