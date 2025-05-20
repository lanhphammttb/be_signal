from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import register, moderate, license, public, record
from app.database import engine, Base
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
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(register.router, prefix="/register", tags=["Register"])
app.include_router(moderate.router, prefix="/moderate", tags=["Moderate"])
app.include_router(license.router, prefix="/license", tags=["License"])
app.include_router(public.router, prefix="/public-records", tags=["Public"])
app.include_router(record.router, prefix="/record", tags=["Record"])