from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from decimal import Decimal

from app.enums.loan_enums import (
    LoanType,
    InterestRateType,
    LoanStatus,
    EmploymentType
)


class LoanApplicationRequest(BaseModel):
    # --- Standard Info ---
    full_name: str
    mobile: str = Field(..., pattern=r"^[6-9]\d{9}$")

    loan_type: LoanType
    requested_amount: Decimal = Field(..., gt=0)
    tenure_months: int = Field(..., ge=6, le=360)
    interest_rate_type: InterestRateType = InterestRateType.FIXED

    # --- Financial Snapshot ---
    monthly_income: Decimal = Field(..., gt=0)
    employment_type: EmploymentType
    organization_name: Optional[str] = None
    existing_monthly_obligations: Decimal = Field(default=0, ge=0)

    # --- VEHICLE ---
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    is_used_vehicle: Optional[bool] = False
    vehicle_registration_number: Optional[str] = None

    # --- GOLD ---
    gold_weight_grams: Optional[Decimal] = None
    gold_purity: Optional[int] = None

    # --- BUSINESS ---
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    gst_number: Optional[str] = None
    business_vintage_years: Optional[int] = None

    # --- HOME ---
    property_type: Optional[str] = None
    property_address_line_1: Optional[str] = None
    property_address_line_2: Optional[str] = None
    property_city: Optional[str] = None
    property_state: Optional[str] = None
    property_pincode: Optional[str] = None
    estimated_property_value: Optional[Decimal] = None

    # --- Consent ---
    consent_given: bool
    
    @model_validator(mode="after")
    def validate_by_loan_type(self):
        #  HOME LOAN
        if self.loan_type == LoanType.HOME:
            if not all([
            self.property_address_line_1,
            self.property_city,
            self.property_state,
            self.property_pincode,
            self.estimated_property_value
        ]):
                raise ValueError("Complete property details required for HOME loan")

        # VEHICLE LOAN
        elif self.loan_type == LoanType.VEHICLE:
            if not self.vehicle_make or not self.vehicle_model:
                raise ValueError("Vehicle make and model required")

            if self.is_used_vehicle is None:
                raise ValueError("Specify if vehicle is used or new")  

      
        #  GOLD LOAN
        elif self.loan_type == LoanType.GOLD:
            if not self.gold_weight_grams or self.gold_weight_grams <= 0:
                raise ValueError("Valid gold weight required")
            
            if not self.gold_purity or self.gold_purity < 18:
                raise ValueError("Valid gold purity required")
            
   
        #  BUSINESS LOAN
        elif self.loan_type == LoanType.BUSINESS:
            if not self.business_name:
                raise ValueError("Business name required")
            
            if not self.gst_number:
                raise ValueError("GST number required")
            
            if not self.business_vintage_years or self.business_vintage_years < 1:
                raise ValueError("Business must be at least 1 year old")
            
        return self
    


class LoanApplyResponse(BaseModel):
    message: str
    loan_id: int


class LoanResponse(BaseModel):
    id: int
    user_id: int

    full_name: str = Field(..., example="Amrita Sharma")
    mobile: str = Field(..., example="9876543210")

    loan_type: LoanType
    requested_amount: Decimal = Field(..., example=500000)
    tenure_months: int = Field(..., example=36)
    interest_rate_type: InterestRateType

    monthly_income: Decimal = Field(..., example=60000)
    employment_type: EmploymentType
    organization_name: Optional[str] = Field(None, example="Infosys")
    existing_monthly_obligations: Decimal = Field(..., example=10000)

    # Vehicle
    vehicle_make: Optional[str] = Field(None, example="Honda")
    vehicle_model: Optional[str] = Field(None, example="City")
    is_used_vehicle: Optional[bool] = Field(None, example=False)
    vehicle_registration_number: Optional[str] = Field(None, example="RJ14AB1234")

    # Gold
    gold_weight_grams: Optional[Decimal] = Field(None, example=50)
    gold_purity: Optional[int] = Field(None, example=22)

    # Business
    business_name: Optional[str] = Field(None, example="ABC Traders")
    business_type: Optional[str] = Field(None, example="Retail")
    gst_number: Optional[str] = Field(None, example="22ABCDE1234F1Z5")
    business_vintage_years: Optional[int] = Field(None, example=5)

    # Home
    property_type: Optional[str] = Field(None, example="Apartment")
    property_address_line_1: Optional[str] = Field(None, example="Sector 21")
    property_address_line_2: Optional[str] = Field(None, example="Near Metro")
    property_city: Optional[str] = Field(None, example="Jaipur")
    property_state: Optional[str] = Field(None, example="Rajasthan")
    property_pincode: Optional[str] = Field(None, example="302017")
    estimated_property_value: Optional[Decimal] = Field(None, example=7500000)

    consent_given: bool = Field(..., example=True)
    consent_timestamp: datetime = Field(..., example="2026-05-01T10:30:00")

    credit_score: Optional[int] = Field(None, example=720)
    foir: Optional[Decimal] = Field(None, example=32.5)
    approved_amount: Optional[Decimal] = Field(None, example=500000)
    interest_rate: Optional[Decimal] = Field(None, example=14.0)
    emi: Optional[Decimal] = Field(None, example=12000)

    status: LoanStatus
    rejection_reason: Optional[str] = Field(None, example="Low credit score")

    created_at: Optional[datetime] = Field(None, example="2026-05-01T10:30:00")
    updated_at: Optional[datetime] = Field(None, example="2026-05-01T11:00:00")

    class Config:
        from_attributes = True


class LoanSummaryResponse(BaseModel):
    loan_id: int
    status: str
    requested_amount: Decimal = Field(..., example=500000)
    approved_amount: Decimal | None = Field(None, example=500000)
    interest_rate: Decimal | None = Field(None, example=14.0)
    credit_score: int | None = Field(None, example=720)
    foir: Decimal | None = Field(None, example=32.5)
    emi: Decimal | None = Field(None, example=12000)

    decision: str
    reason: str | None

    class Config:
        from_attributes = True