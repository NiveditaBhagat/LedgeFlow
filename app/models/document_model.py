from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy import Enum as SQLAlchemyEnum
from app.database import Base
from app.enums.doc_enums import DocumentStatus, DocumentType


class UserDocument(Base):
    __tablename__ = "user_documents"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    document_type = Column(SQLAlchemyEnum(DocumentType), nullable=False)
    file_name= Column(String,nullable=False)
    file_path = Column(String,nullable=False)       # actual file

    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    remarks=Column(String, nullable=True)

    __table_args__ = (
        # Guardrail: Only one active document of a specific type per user
        UniqueConstraint('user_id', 'document_type', 'is_active', name='_user_doc_active_uc'),
    )