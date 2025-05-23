from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import copyright, moderate, license, auth, public
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

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(copyright.router, prefix="/copyright", tags=["Copyright"])
app.include_router(moderate.router, prefix="/moderate", tags=["Moderate"])
app.include_router(license.router, prefix="/license", tags=["License"])
app.include_router(public.router, prefix="/public", tags=["Public"])
