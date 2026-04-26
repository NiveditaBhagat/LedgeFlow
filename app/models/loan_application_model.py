from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.sql import func
import enum

from app.database import Base


class LoanStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISBURSED = "DISBURSED"


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)

    #  user link
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    #  borrower snapshot (don’t rely only on user table)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    pan_number = Column(String, nullable=False)
  

    #  Avoid storing Aadhaar raw (skip or encrypt if needed)

    #  loan request
    loan_type = Column(String, nullable=False)
    requested_amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    loan_purpose = Column(String, nullable=True)
    interest_rate_type = Column(String, nullable=False)

    #  financial profile
    monthly_income = Column(Float, nullable=False)
    employment_type = Column(String, nullable=False)
    organization_name = Column(String, nullable=True)
    existing_monthly_obligations = Column(Float, default=0)

    #  credit decision inputs/outputs
    credit_score = Column(Integer, nullable=True)
    approved_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)

    #  consent tracking (VERY IMPORTANT)
    consent_given = Column(Boolean, nullable=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)

    #  lifecycle
    status = Column(Enum(LoanStatus), default=LoanStatus.INITIATED, nullable=False)
    rejection_reason = Column(Text, nullable=True)

    #  timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())