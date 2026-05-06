import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.database import Base


class VerificationStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class AccountType(str, enum.Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"


class UserBankDetails(Base):
    __tablename__ = "user_bank_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Input
    account_holder_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False, unique=True)
    bank_name = Column(String, nullable=False)
    ifsc_code = Column(String, nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.SAVINGS)

    # Verification lifecycle
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.SUBMITTED)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_name_from_bank = Column(String, nullable=True)
    verification_reference_id = Column(String, nullable=True)

    # Usage
    is_primary = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())