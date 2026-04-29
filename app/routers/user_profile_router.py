from app.database import get_db
from app.core.security import get_current_user
from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.models.user_profile_model import UserProfile,KYCStatus
from app.models.user_model import User,UserRole
from app.schemas.user_profile_schema import UserProfileCreate,UserProfileResponse, UserProfileUpdate
from starlette import status


router=APIRouter(
    prefix='/user_profile',
    tags=['user_profile']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    db: db_dependency,
    current_user: user_dependency
):
    if current_user.role !=UserRole.BORROWER:
        raise HTTPException(status_code=403, detail="Access denied. Only BORROWER accounts can create a profile.")
    
    existing_profile=db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if existing_profile:
        raise HTTPException(status_code=400,detail="Profile already exists for this user.")
    
    new_user_profile=UserProfile(
        **profile_data.model_dump(),
        user_id=current_user.id,
        kyc_status=KYCStatus.PENDING
    )

    db.add(new_user_profile)
    db.commit()
    db.refresh(new_user_profile)

    return new_user_profile

@router.get("/get_user_profile", response_model=UserProfileResponse)
async def get_user_profile(db: db_dependency, current_user: user_dependency):
    if current_user.role !=UserRole.BORROWER:
        raise HTTPException(status_code=403, detail="Access denied. Only BORROWER accounts can access profile.")
    profile=db.query(UserProfile).filter(UserProfile.user_id==current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.patch("/update")
def update_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role !=UserRole.BORROWER:
        raise HTTPException(status_code=403, detail="Access denied. Only BORROWER accounts can update a profile.")
    
    db_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not db_profile:
        raise HTTPException(404, "Profile not found")

    update_data = profile_data.model_dump(exclude_unset=True)



    for key, value in update_data.items():
        setattr(db_profile, key, value)

    # if any(field in update_data for field in kyc_sensitive_fields):
    #     # Only reset if it was previously VERIFIED to avoid unnecessary updates
    #     if db_profile.kyc_status == KYCStatus.VERIFIED:
    #         db_profile.kyc_status = KYCStatus.PENDING 

    #  Reset KYC if ANY update happens
    if update_data and db_profile.kyc_status == KYCStatus.VERIFIED:
        db_profile.kyc_status = KYCStatus.PENDING

    db.commit()
    db.refresh(db_profile)

    return db_profile