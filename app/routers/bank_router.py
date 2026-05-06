#API endpoints
from app.database import get_db
from app.core.security import get_current_user
from datetime import timedelta, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.models.user_profile_model import UserProfile,KYCStatus
from app.models.bank_details_model import UserBankDetails, VerificationStatus
from app.models.user_model import UserRole
from app.schemas.bank_detail_schema import UserBankDetailsCreate, UserBankDetailsResponse
from starlette import status
from app.enums.loan_enums import  LoanStatus
from datetime import datetime

from app.services.bank_service import BankVerificationService


router=APIRouter(
    prefix='/bank_detail',
    tags=['bank_detail']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.post("/", response_model=UserBankDetailsResponse)
def add_bank_details(
    bank_data: UserBankDetailsCreate,
    db: db_dependency,
    current_user: user_dependency
):
    #  Only borrower can add bank
    if current_user.role != UserRole.BORROWER:
        raise HTTPException(403, "Only borrower can add bank details")

    #prevent duplicate account number
    existing = db.query(UserBankDetails).filter(
        UserBankDetails.account_number == bank_data.account_number
    ).first()

    if existing:
        raise HTTPException(400, "Bank account already exists")

    # Handle primary account logic
    if bank_data.is_primary:
        db.query(UserBankDetails).filter(
            UserBankDetails.user_id == current_user.id
        ).update({"is_primary": False})

    # Create new bank record
    new_bank = UserBankDetails(
        user_id=current_user.id,
        account_holder_name=bank_data.account_holder_name,
        account_number=bank_data.account_number,
        bank_name=bank_data.bank_name,
        ifsc_code=bank_data.ifsc_code,
        account_type=bank_data.account_type,
        is_primary=bank_data.is_primary,
        verification_status=VerificationStatus.SUBMITTED
    )

    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)

    return new_bank








@router.post("/{bank_id}/verify")
def verify_bank_account(
    bank_id: int,
    db: db_dependency,
    current_user: user_dependency
):
    # Only borrower
    if current_user.role != UserRole.BORROWER:
        raise HTTPException(403, "Only borrower can verify bank account")

    #  Fetch bank
    bank = db.query(UserBankDetails).filter(
        UserBankDetails.id == bank_id
    ).first()

    if not bank:
        raise HTTPException(404, "Bank details not found")

    # Ownership check
    if bank.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    #  Already verified
    if bank.verification_status == VerificationStatus.VERIFIED:
        raise HTTPException(400, "Bank already verified")

    #  Fetch profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(404, "User profile not found")

    #  USE SERVICE HERE
    result = BankVerificationService.verify_account(
        profile.full_name,
        bank.account_holder_name
    )

    # Update DB based on result
    bank.verification_status = result["status"]
    bank.verified_name_from_bank = result["verified_name"]
    bank.verification_reference_id = result["reference_id"]

    if result["status"] == VerificationStatus.VERIFIED:
        bank.verified_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(bank)

    return {
        "bank_id": bank.id,
        "status": bank.verification_status,
        "reference_id": bank.verification_reference_id,
        "match_score": result["score"]   
    }


@router.get("/", response_model=list[UserBankDetailsResponse])
def get_my_banks(
    db: db_dependency,
    current_user: user_dependency
):
    if current_user.role != UserRole.BORROWER:
        raise HTTPException(403, "Only borrower can view bank details")

    banks = db.query(UserBankDetails).filter(
        UserBankDetails.user_id == current_user.id,
        UserBankDetails.is_active == True
    ).order_by(UserBankDetails.created_at.desc()).all()

    return banks

@router.get("/primary", response_model=UserBankDetailsResponse)
def get_primary_bank(
    db: db_dependency,
    current_user: user_dependency
):
    if current_user.role != UserRole.BORROWER:
        raise HTTPException(403, "Only borrower can view bank details")

    bank = db.query(UserBankDetails).filter(
        UserBankDetails.user_id == current_user.id,
        UserBankDetails.is_primary == True,
        UserBankDetails.is_active == True
    ).first()

    if not bank:
        raise HTTPException(404, "Primary bank not found")
    

    return bank


@router.get("/{bank_id}", response_model=UserBankDetailsResponse)
def get_bank_by_id(
    bank_id: int,
    db: db_dependency,
    current_user: user_dependency
):
    bank = db.query(UserBankDetails).filter(
        UserBankDetails.id == bank_id
    ).first()

    if not bank:
        raise HTTPException(404, "Bank not found")

    # Access control
    if current_user.role == UserRole.BORROWER:
        if bank.user_id != current_user.id:
            raise HTTPException(403, "Access denied")

    elif current_user.role not in [UserRole.ADMIN, UserRole.CREDIT]:
        raise HTTPException(403, "Access denied")

    return bank


