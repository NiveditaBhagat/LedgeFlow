import shutil
from typing import Annotated
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.enums.doc_enums import DocumentStatus, DocumentType
from app.models.document_model import UserDocument

router=APIRouter(
    prefix='/docs',
    tags=['docs']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/documents/upload")
async def upload_document(
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1. Check if a document of this type already exists and is active
    existing_doc = db.query(UserDocument).filter(
        UserDocument.user_id == current_user.id,
        UserDocument.document_type == document_type,
        UserDocument.is_active == True
    ).first()

    # 2. Prepare the file storage
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    user_folder = Path(UPLOAD_DIR) / str(current_user.id)
    user_folder.mkdir(parents=True, exist_ok=True)
    file_path = user_folder / unique_filename

    try:
        # 3. Handle the "Supersede" Logic within a transaction
        if existing_doc:
            # Soft delete: Deactivate the old version
            existing_doc.is_active = False 
            # Optional: Move status to 'ARCHIVED' or similar if you add that enum
        
        # Save the physical file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create the new record
        new_doc = UserDocument(
            user_id=current_user.id,
            document_type=document_type,
            file_name=file.filename,
            file_path=str(file_path),
            is_active=True, # This is the current one
            status=DocumentStatus.UPLOADED
        )

        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        return {
            "message": f"{document_type.value} uploaded successfully.",
            "document_id": new_doc.id,
            "superseded_old_version": True if existing_doc else False
        }

    except Exception as e:
        db.rollback()
        # Clean up the file if DB save fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        file.file.close()