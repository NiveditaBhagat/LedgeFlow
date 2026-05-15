from typing import Optional

from pydantic import BaseModel
from app.enums.doc_enums import DocumentType, DocumentStatus


class DocumentUploadResponse(BaseModel):
    id: int
    document_type: DocumentType
    file_path: str
    status: DocumentStatus
    is_active: bool
    remarks: Optional[str] = None
 
    class Config:
        from_attributes = True


class DocumentReviewRequest(BaseModel):
    status: DocumentStatus
    remarks: str