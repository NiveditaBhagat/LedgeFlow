#The Pydantic Classes
from pydantic import BaseModel, Field, field_validator,model_validator
from typing import Optional
from decimal import Decimal
from datetime import date, datetime
from enum import Enum

from app.models.user_model import UserRole


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
    full_name: str = Field(..., min_length=3, max_length=100,pattern=r"^[A-Za-z ]+$")

    mobile: str = Field(
        ...,
        pattern=r"^[6-9]\d{9}$",
        description="10-digit Indian mobile number"
    )
    date_of_birth: date
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
    pincode: str = Field(..., pattern=r"^\d{6}$")


    @model_validator(mode="after")
    def validate_employment(self):

        if (
            self.employment_type == EmploymentType.SALARIED
            and not self.organization_name
            ):
            raise ValueError(
                "organization_name is required for salaried users"
            )

        return self

    # Ensure PAN is uppercase
    @field_validator("pan_number")
    @classmethod
    def uppercase_pan(cls, v: str):
        return v.upper()


    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date):
        if v is None:
            return v
        
        # Calculate age
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        # KYC rule: Borrower must be 18+
        if age < 18:
            raise ValueError("You must be at least 18 years old to apply for a loan.")
        
        # Safety check: DOB cannot be in the future
        if v > today:
            raise ValueError("Date of birth cannot be in the future.")
            
        return v
   

    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "Rahul Sharma",
                "mobile": "9876543210",
                "date_of_birth": "1998-05-12",
                "pan_number": "ABCDE1234F",
                "aadhaar_number": "123456789012",
                "employment_type": "SALARIED",
                "organization_name": "Infosys",
                "monthly_income": 75000,
                "existing_monthly_obligations": 12000,
                "address_line_1": "221B MG Road",
                "address_line_2": "Near Metro Station",
                "city": "Jaipur",
                "state": "Rajasthan",
                "pincode": "302001"
            }
        }
    }







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
    date_of_birth: Optional[date] = None 
    organization_name: Optional[str] = None

    monthly_income: Optional[Decimal] = Field(None, gt=0)
    existing_monthly_obligations: Optional[Decimal] = Field(None, ge=0)

    employment_type: Optional[EmploymentType] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = Field(None, pattern=r"^\d{6}$")

    @model_validator(mode="after")
    def validate_employment(cls, values):
        emp_type = values.employment_type
        org = values.organization_name

        if emp_type == "SALARIED" and not org:
            raise ValueError("organization_name is required for salaried users")

        return values
    
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date):
        if v is None:
            return v
        
        # Calculate age
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        # KYC rule: Borrower must be 18+
        if age < 18:
            raise ValueError("You must be at least 18 years old to apply for a loan.")
        
        # Safety check: DOB cannot be in the future
        if v > today:
            raise ValueError("Date of birth cannot be in the future.")
            
        return v


class UpdateUserRoleRequest(BaseModel):
    role: UserRole
    