#The Pydantic Classes
from pydantic import BaseModel, Field, field_validator,model_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


# Enums
class KYCStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class EmploymentType(str, Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"


# Base Schema (shared fields)
class UserProfileBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)

    mobile: str = Field(
        ...,
        pattern=r"^[6-9]\d{9}$",
        description="10-digit Indian mobile number"
    )

    pan_number: str = Field(
        ...,
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
        description="PAN format"
    )

    aadhaar_number: str = Field(
        ...,
        pattern=r"^\d{12}$",
        description="12-digit Aadhaar"
    )

    employment_type: EmploymentType
    organization_name: Optional[str] = None

    monthly_income: Decimal = Field(..., gt=0)
    existing_monthly_obligations: Decimal = Field(default=Decimal("0.0"), ge=0)

    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    pincode: str
    # Ensure PAN is uppercase
    @field_validator("pan_number")
    @classmethod
    def uppercase_pan(cls, v: str):
        return v.upper()


# Schema for Creating Profile (Request)
class UserProfileCreate(UserProfileBase):
    pass


# Schema for Response (Output)
class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    kyc_status: KYCStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)

    mobile: Optional[str] = Field(
        None,
        pattern=r"^[6-9]\d{9}$"
    )

    organization_name: Optional[str] = None

    monthly_income: Optional[Decimal] = Field(None, gt=0)
    existing_monthly_obligations: Optional[Decimal] = Field(None, ge=0)

    employment_type: Optional[EmploymentType] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    pincode: str

    @model_validator(mode="after")
    def validate_employment(cls, values):
        emp_type = values.employment_type
        org = values.organization_name

        if emp_type == "SALARIED" and not org:
            raise ValueError("organization_name is required for salaried users")

        return values

    