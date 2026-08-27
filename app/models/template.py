import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    preview_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())