from app.database import get_db
from app.core.security import get_current_user
from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.models.user_profile_model import UserProfile,KYCStatus
from app.models.user_model import User,UserRole
from app.services.kyc_service import mock_verify_pan


router=APIRouter(
    prefix='/kyc',
    tags=['kyc']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.post("/verify-kyc")
async def verify_kyc(db:db_dependency, current_user:user_dependency):

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile.kyc_status == KYCStatus.VERIFIED:
        return {"message": "KYC already verified"}
    
    if profile.kyc_status == KYCStatus.REJECTED:
        return {"message": "KYC already rejected. Please update details."}
    
    result = mock_verify_pan(profile.pan_number)

    if result["status"] == "VALID":
        profile.kyc_status = KYCStatus.VERIFIED
    else:
        profile.kyc_status = KYCStatus.REJECTED

    db.commit()

    return {
        "kyc_status": profile.kyc_status,
        "provider_response": result
    }


