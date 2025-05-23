from app.core.auth import ALGORITHM
from app.core.constaint import SECRET_KEY
from app.utils.crypto import generate_rsa_key_pair
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.schemas import UserCreate, TokenResponse
from app.database import get_session
from app.models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    q = await session.execute(select(User).where(User.username == form_data.username))
    user = q.scalars().first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    payload = {"sub": user.username, "user_id": user.id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, session: AsyncSession = Depends(get_session)):
    q = await session.execute(select(User).where(User.username == user_create.username))
    existing_user = q.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username đã tồn tại")

    hashed_password = pwd_context.hash(user_create.password)
    private_pem, public_pem = generate_rsa_key_pair()

    user = User(
        username=user_create.username,
        hashed_password=hashed_password,
        public_key_pem=public_pem
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Trả private key cho user (bạn có thể gửi qua email hoặc UI tải file)
    return {"msg": "Đăng ký thành công", "private_key": private_pem}
