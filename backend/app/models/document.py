import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Enum, Integer, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.db import Base
from app.models.enums import DocumentStatusEnum


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DocumentStatusEnum] = mapped_column(Enum(DocumentStatusEnum, name="document_status_enum"),
                                                       nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="documents")
    uploader = relationship("User", back_populates="documents")
