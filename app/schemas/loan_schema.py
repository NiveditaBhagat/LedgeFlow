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

    # 🔥 Validation based on loan type
    @model_validator(mode="after")
    def validate_by_loan_type(self):
        if self.loan_type == LoanType.HOME:
            if not self.property_address_line_1 or not self.property_city:
                raise ValueError("Property details required for HOME loan")

        if self.loan_type == LoanType.VEHICLE:
            if not self.vehicle_model:
                raise ValueError("Vehicle details required for VEHICLE loan")

        if self.loan_type == LoanType.GOLD:
            if not self.gold_weight_grams or not self.gold_purity:
                raise ValueError("Gold details required for GOLD loan")

        if self.loan_type == LoanType.BUSINESS:
            if not self.business_name:
                raise ValueError("Business details required for BUSINESS loan")

        return self
    


class LoanApplyResponse(BaseModel):
    message: str
    loan_id: int


class LoanResponse(BaseModel):
    id: int
    user_id: int

    full_name: str
    mobile: str

    loan_type: LoanType
    requested_amount: Decimal
    tenure_months: int
    interest_rate_type: InterestRateType

    monthly_income: Decimal
    employment_type: EmploymentType
    organization_name: Optional[str]
    existing_monthly_obligations: Decimal

    # Vehicle
    vehicle_make: Optional[str]
    vehicle_model: Optional[str]
    is_used_vehicle: Optional[bool]
    vehicle_registration_number: Optional[str]

    # Gold
    gold_weight_grams: Optional[Decimal]
    gold_purity: Optional[int]

    # Business
    business_name: Optional[str]
    business_type: Optional[str]
    gst_number: Optional[str]
    business_vintage_years: Optional[int]

    # Home
    property_type: Optional[str]
    property_address_line_1: Optional[str]
    property_address_line_2: Optional[str]
    property_city: Optional[str]
    property_state: Optional[str]
    property_pincode: Optional[str]
    estimated_property_value: Optional[Decimal]

    consent_given: bool
    consent_timestamp: datetime

    credit_score: Optional[int]
    foir: Optional[Decimal]
    approved_amount: Optional[Decimal]
    interest_rate: Optional[Decimal]
    emi: Optional[Decimal]

    status: LoanStatus
    rejection_reason: Optional[str]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LoanSummaryResponse(BaseModel):
    loan_id: int
    status: str
    requested_amount: Decimal
    approved_amount: Optional[Decimal]

    credit_score: Optional[int]
    foir: Optional[Decimal]
    emi: Optional[Decimal]

    decision: str
    reason: Optional[str]

    class Config:
        from_attributes = True