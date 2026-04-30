#API endpoints
from app.database import get_db
from app.core.security import get_current_user
from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.models.user_profile_model import UserProfile,KYCStatus
from app.models.loan_application_model import LoanApplication
from app.models.user_model import UserRole
from app.schemas.loan_schema import LoanApplicationRequest,LoanApplyResponse
from starlette import status
from app.enums.loan_enums import  LoanStatus
from datetime import datetime

router=APIRouter(
    prefix='/loans',
    tags=['Loans']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.post("/apply",status_code=status.HTTP_201_CREATED)
async def apply_loan( loan_request: LoanApplicationRequest,db: db_dependency,current_user:user_dependency):

    if current_user.role != UserRole.BORROWER:
        raise HTTPException(
            status_code=403,
            detail="Only borrowers can apply for loans"
        )
    
    if not loan_request.consent_given:
        raise HTTPException(
            status_code=400, detail="Consent is required to proceed"
        )
    
    loan = LoanApplication(
        user_id=current_user.id,

        # --- Standard Info ---
        full_name=loan_request.full_name,
        mobile=loan_request.mobile,

        loan_type=loan_request.loan_type,
        requested_amount=loan_request.requested_amount,
        tenure_months=loan_request.tenure_months,
        interest_rate_type=loan_request.interest_rate_type,

        # --- Financial Snapshot ---
        monthly_income=loan_request.monthly_income,
        employment_type=loan_request.employment_type,
        organization_name=loan_request.organization_name,
        existing_monthly_obligations=loan_request.existing_monthly_obligations,

        # --- Vehicle ---
        vehicle_make=loan_request.vehicle_make,
        vehicle_model=loan_request.vehicle_model,
        is_used_vehicle=loan_request.is_used_vehicle,
        vehicle_registration_number=loan_request.vehicle_registration_number,

        # --- Gold ---
        gold_weight_grams=loan_request.gold_weight_grams,
        gold_purity=loan_request.gold_purity,

        # --- Business ---
        business_name=loan_request.business_name,
        business_type=loan_request.business_type,
        gst_number=loan_request.gst_number,
        business_vintage_years=loan_request.business_vintage_years,

        # --- Home ---
        property_type=loan_request.property_type,
        property_address_line_1=loan_request.property_address_line_1,
        property_address_line_2=loan_request.property_address_line_2,
        property_city=loan_request.property_city,
        property_state=loan_request.property_state,
        property_pincode=loan_request.property_pincode,
        estimated_property_value=loan_request.estimated_property_value,

        # --- Consent ---
        consent_given=True,
        consent_timestamp=datetime.utcnow(),

        # --- Status ---
        status=LoanStatus.INITIATED
    )

    db.add(loan)
    db.commit()
    db.refresh(loan)

    return LoanApplyResponse(
        message="Loan application submitted successfully",
        loan_id=loan.id
    )
    
