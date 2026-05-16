import shutil
from typing import Annotated, List
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.enums.doc_enums import DOCUMENT_REVIEW_ACCESS, DocumentStatus, DocumentType
from app.enums.loan_enums import LoanStatus
from app.models.document_model import UserDocument
from app.models.loan_application_model import LoanApplication
from app.models.user_model import UserRole
from app.models.user_profile_model import KYCStatus, UserProfile
from app.schemas.doc_upload_schema import DocumentReviewRequest, DocumentUploadResponse

router=APIRouter(
    prefix='/docs',
    tags=['docs']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

KYC_DOCS = [
    DocumentType.PAN,
    DocumentType.AADHAR
]


ALLOWED_EXTENSIONS = [
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png"
]

MAX_FILE_SIZE = 5 * 1024 * 1024   # 5 MB


@router.post("/documents/upload")
async def upload_document(
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    if current_user.role != UserRole.BORROWER:
        raise HTTPException(
            status_code=403,
            detail="Only borrowers can upload documents"
        )
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Complete profile before uploading documents"
        )
    
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )
    
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="File size exceeds 5 MB limit"
        )

    file.file.seek(0)

    
    if document_type in KYC_DOCS:
        if profile.kyc_status==KYCStatus.VERIFIED:
            raise HTTPException(
                status_code=400,
                detail="KYC already verified"
            )

    # Other docs require loan application
    if document_type not in KYC_DOCS:

        if not profile.kyc_status==KYCStatus.VERIFIED:
            raise HTTPException(
            status_code=400,
            detail="Complete KYC first"
            )

        loan = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id
        ).first()

        if not loan:
            raise HTTPException(
            status_code=400,
            detail="Apply for loan first"
            )
        
        if loan.status not in [LoanStatus.INITIATED, LoanStatus.UNDER_REVIEW]:
            raise HTTPException(
            status_code=400,
            detail="Documents cannot be uploaded at this stage"
            )
   
    
    #  Check if a document of this type already exists and is active
    existing_doc = db.query(UserDocument).filter(
        UserDocument.user_id == current_user.id,
        UserDocument.document_type == document_type,
        UserDocument.is_active == True
    ).first()

    #  Prepare the file storage
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    user_folder = Path(UPLOAD_DIR) / str(current_user.id)
    user_folder.mkdir(parents=True, exist_ok=True)
    file_path = user_folder / unique_filename

    try:
        
        if existing_doc:
            # Soft delete: Deactivate the old version
            existing_doc.is_active = False 
            
        
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





@router.get("/my_docs",response_model=List[DocumentUploadResponse])
async def get_my_documents(db: db_dependency, current_user: user_dependency):
    if current_user.role!=UserRole.BORROWER:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: This endpoint is for borrowers only."
        )
    
    docs = db.query(UserDocument).filter(
        UserDocument.user_id == current_user.id,
        UserDocument.is_active == True
    ).all()

    return docs




@router.get("/{user_id}/documents", response_model=List[DocumentUploadResponse])
async def get_user_documents(db: db_dependency, current_user: user_dependency, user_id: int):
    if current_user.role not in [UserRole.ADMIN, UserRole.OPS]:
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Admin or Ops access required"
        )
    
    docs = db.query(UserDocument).filter(
        UserDocument.user_id == user_id,
        UserDocument.is_active == True
    ).order_by(
        UserDocument.created_at.desc()  # Then most recent first
    ).all()

    if not docs:
        raise HTTPException(
            status_code=404, 
            detail=f"No active documents found for user {user_id}"
        )

    return docs



@router.patch("/{doc_id}/review")
async def review_document(
    review_data: DocumentReviewRequest,
    db: db_dependency,
    current_user: user_dependency,
    doc_id: int
):

    doc = db.query(UserDocument).filter(
        UserDocument.id == doc_id,
        UserDocument.is_active == True
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # role access check
    allowed_roles = DOCUMENT_REVIEW_ACCESS.get(
        doc.document_type,
        []
    )

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to review this document"
        )

    # prevent reviewing already verified docs
    if doc.status == DocumentStatus.VERIFIED:
        raise HTTPException(
            status_code=400,
            detail="Document already verified"
        )

    doc.status = review_data.status
    doc.remarks = review_data.remarks

    db.commit()
    db.refresh(doc)

    return {
        "message": f"Document status updated to {review_data.status}",
        "document_id": doc.id,
        "document_type": doc.document_type,
        "status": doc.status,
        "remarks": doc.remarks
    }




@router.delete("/{document_id}")
async def deactivate_document(
    document_id: int,
    db: db_dependency,
    current_user: user_dependency
):

    document = db.query(UserDocument).filter(
        UserDocument.id == document_id,
        UserDocument.is_active == True
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    profile=db.query(UserProfile).filter(UserProfile.user_id==current_user.id).first()
    # BORROWER ACCESS
    if current_user.role == UserRole.BORROWER:

        # borrower can access only own docs
        if document.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not allowed"
            )

 
        # KYC DOCUMENTS
        if document.document_type in KYC_DOCS:

            # once kyc verified -> locked
            if profile.kyc_status==KYCStatus.VERIFIED:
                raise HTTPException(
                    status_code=400,
                    detail="KYC documents are locked after verification"
                )

            # only rejected docs can be replaced
            if document.status != DocumentStatus.REJECTED:
                raise HTTPException(
                    status_code=400,
                    detail="Only rejected KYC documents can be deactivated"
                )

  
        # LOAN DOCUMENTS
        else:

            loan = db.query(LoanApplication).filter(
                LoanApplication.user_id == current_user.id
            ).first()

            if not loan:
                raise HTTPException(
                    status_code=400,
                    detail="Loan application not found"
                )

            # only editable in early stages
            if loan.status not in [
                LoanStatus.INITIATED,
                LoanStatus.UNDER_REVIEW
            ]:
                raise HTTPException(
                    status_code=400,
                    detail="Loan documents are locked at this stage"
                )

            # only rejected docs can be changed
            if document.status != DocumentStatus.REJECTED:
                raise HTTPException(
                    status_code=400,
                    detail="Only rejected loan documents can be deactivated"
                )

   
    # ADMIN / OPS ACCESS
    elif current_user.role not in [
        UserRole.ADMIN,
        UserRole.OPS
    ]:
        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )

  
    # DEACTIVATE DOCUMENT
    document.is_active = False

    db.commit()

    return {
        "message": "Document deactivated successfully"
    }