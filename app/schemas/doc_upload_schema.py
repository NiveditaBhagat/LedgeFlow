from pydantic import BaseModel
from app.enums.doc_enums import DocumentType, DocumentStatus


class DocumentUploadResponse(BaseModel):
    id: int
    document_type: DocumentType
    file_path: str
    status: DocumentStatus

    class Config:
        from_attributes = True