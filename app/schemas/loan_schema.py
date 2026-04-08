#The Pydantic Classes

from fastapi import FastAPI,APIRouter
from pydantic import BaseModel,EmailStr, Field
from enum import Enum
from typing import Optional

router= APIRouter()

#  Enums for Product Configuration
class EmploymentType(str,Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"

class InterestRateType(str, Enum):
    FIXED = "FIXED"
    FLOATING = "FLOATING"

class LoanType(str, Enum):
    PERSONAL = "PERSONAL"
    HOME = "HOME"
    VEHICLE = "VEHICLE"
    GOLD = "GOLD"


class BorrowerInfo(BaseModel):
    full_name: str = Field(..., example="Rahul Sharma")
    email: EmailStr
    mobile: str = Field(..., pattern=r"^[6-9]\d{9}$", description="10-digit Indian Mobile")
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", description="Standard PAN format")
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$", description="12-digit Aadhaar")

class FinancialProfile(BaseModel):
    monthly_income: float = Field(..., gt=0)
    employment_type: EmploymentType
    organization_name: Optional[str] = None # Optional for self-employed
    existing_monthly_obligations: float = Field(default=0, ge=0)

class LoanRequest(BaseModel):
    loan_type: LoanType
    requested_amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., ge=6, le=360)
    loan_purpose: str
    rate_type: InterestRateType = InterestRateType.FIXED # User only picks the behavior


# The Root Schema for the JSON Request
class LoanApplicationRequest(BaseModel):
    borrower_info: BorrowerInfo
    financial_profile: FinancialProfile
    loan_request: LoanRequest


@router.post("/")
async def root():
    return {"message": "Hello World55 "}