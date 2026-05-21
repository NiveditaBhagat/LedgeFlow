from app.database import get_db
from app.core.security import get_current_user
from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.enums.doc_enums import DocumentStatus, DocumentType
from app.models.document_model import UserDocument
from app.models.user_profile_model import UserProfile,KYCStatus
from app.models.user_model import User,UserRole
from app.services.kyc_service import KYCService
from app.services.sandbox.auth_service import SandboxKYCProvider
from app.services.mock_kyc_service import MockKYCProvider

router=APIRouter(
    prefix='/kyc',
    tags=['kyc']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.post("/verify-kyc/{user_id}")
async def verify_kyc(user_id: int,db:db_dependency, current_user:user_dependency):

      #  Only CREDIT / OPS allowed
    if current_user.role not in [UserRole.ADMIN, UserRole.OPS]:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # if profile.kyc_status == KYCStatus.PENDING:
    #     return {"message": "KYC verification is in progress. Please check back late. "}
    
    if profile.kyc_status == KYCStatus.VERIFIED:
        return {"message": "KYC already verified"}
    
    if profile.kyc_status == KYCStatus.REJECTED:
        return {"message": "KYC already rejected. Please update details."}
    

    pan_doc = db.query(UserDocument).filter(
    UserDocument.user_id == user_id,
    UserDocument.document_type == DocumentType.PAN,
    UserDocument.status == DocumentStatus.VERIFIED,
    UserDocument.is_active == True
    ).first()

    

    aadhaar_doc = db.query(UserDocument).filter(
        UserDocument.user_id == user_id,
        UserDocument.document_type == DocumentType.AADHAR,
        UserDocument.status == DocumentStatus.VERIFIED,
        UserDocument.is_active == True
    ).first()

    if not pan_doc or not aadhaar_doc:
        raise HTTPException(
            status_code=400,
            detail="PAN and AADHAR documents are required"
        )
    
    if pan_doc.status == DocumentStatus.REJECTED:
        raise HTTPException(
            status_code=400,
            detail="PAN document rejected"
        )

    if pan_doc.status in [
        DocumentStatus.UPLOADED,
        DocumentStatus.UNDER_REVIEW
    ]:
        raise HTTPException(
            status_code=400,
            detail="PAN document verification pending"
        )
    
    if aadhaar_doc.status == DocumentStatus.REJECTED:
        raise HTTPException(
            status_code=400,
            detail="AADHAAR document rejected"
        )

    if aadhaar_doc.status in [
        DocumentStatus.UPLOADED,
        DocumentStatus.UNDER_REVIEW
    ]:
        raise HTTPException(
            status_code=400,
            detail="AADHAAR document verification pending"
        )

    result = KYCService.verify_pan(
    pan_number=profile.pan_number,
    full_name=profile.full_name,
    dob=profile.date_of_birth.strftime("%d/%m/%Y")
    )

   
    
    print(result)
    data = result.get("data", {})

    # Verification checks
    is_verified = (
        data.get("status") == "valid"
        and data.get("name_as_per_pan_match") is True
        and data.get("date_of_birth_match") is True
    )
    
    if is_verified:
        profile.kyc_status = KYCStatus.VERIFIED
    else:
        profile.kyc_status = KYCStatus.REJECTED

    db.commit()
    db.refresh(profile)

    return {
        "user_id": user_id,
        "kyc_status": profile.kyc_status,
        "provider_response": result
    }


# @router.get("/sandbox-auth-test")
# def sandbox_auth_test():

#     token = SandboxKYCProvider.get_access_token()

#     return {
#         "access_token": token
#     }
