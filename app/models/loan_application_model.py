from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text, Numeric
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

    #  User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    #  Minimal snapshot (for UI / audit)
    full_name = Column(String, nullable=False)
    mobile = Column(String, nullable=False)

    #  Loan request
    loan_type = Column(String, nullable=False)
    requested_amount = Column(Numeric(12, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    loan_purpose = Column(String, nullable=True)
    interest_rate_type = Column(String, nullable=False)

    #  Financial snapshot (at time of application)
    monthly_income = Column(Numeric(12, 2), nullable=False)
    employment_type = Column(String, nullable=False)
    organization_name = Column(String, nullable=True)
    existing_monthly_obligations = Column(Numeric(12, 2), default=0)

    #  Decision fields (filled later)
    credit_score = Column(Integer, nullable=True)
    approved_amount = Column(Numeric(12, 2), nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)

    #  Consent (for CIBIL check)
    consent_given = Column(Boolean, nullable=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=False)

    #  Status lifecycle
    status = Column(Enum(LoanStatus), default=LoanStatus.INITIATED, nullable=False)
    rejection_reason = Column(Text, nullable=True)

    #  Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())