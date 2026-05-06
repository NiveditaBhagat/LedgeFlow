from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, field_serializer, field_validator
from enum import Enum
import re

from app.models.bank_details_model import AccountType, VerificationStatus

IST = ZoneInfo("Asia/Kolkata")


class UserBankDetailsCreate(BaseModel):
    account_holder_name: str = Field(..., min_length=3, max_length=100)

    account_number: str = Field(
        ...,
        min_length=9,
        max_length=18
    )

    bank_name: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    ifsc_code: str = Field(
        ...,
        pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$"
    )

    account_type: AccountType = AccountType.SAVINGS
    is_primary: bool = True

    # validations
    @field_validator("account_holder_name")
    @classmethod
    def validate_name(cls, v: str):
        if not re.match(r"^[A-Za-z ]+$", v):
            raise ValueError("Invalid name format")
        return v.strip().title()

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, v: str):
        if not v.isdigit():
            raise ValueError("Account number must be digits only")
        return v

    @field_validator("bank_name")
    @classmethod
    def validate_bank_name(cls, v: str):
        return v.strip().title()
    

class UserBankDetailsResponse(BaseModel):
    id: int
    user_id: int

    account_holder_name: str
    account_number: str
    bank_name: str
    ifsc_code: str
    account_type: AccountType

    verification_status: VerificationStatus
    verified_at: Optional[datetime]
    verified_name_from_bank: Optional[str]
    verification_reference_id: Optional[str]

    is_primary: bool
    is_active: bool

    created_at: datetime

    #  Mask account number (important)
    @field_validator("account_number")
    @classmethod
    def mask_account_number(cls, v: str):
        return "XXXXXX" + v[-4:]

    @field_serializer("verified_at", "created_at")
    def convert_to_ist(self, value: datetime):
        if value is None:
            return value
        return value.astimezone(IST)
    
    class Config:
        from_attributes = True