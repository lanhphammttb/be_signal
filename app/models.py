from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text
from .database import Base
# DB model
class CopyrightRecord(Base):
    __tablename__ = "copyright_records"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    blockchain_tx_hash = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    approved = Column(Boolean, default=False)
    owner_address = Column(String, nullable=True)