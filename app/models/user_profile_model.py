# Database Tables (SQLAlchemy Models)
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Date


# KYC Status Enum
class KYCStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


# Employment Type Enum
class EmploymentType(str, enum.Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    # Link to User (One-to-One via unique constraint)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Personal Info
    full_name = Column(String, nullable=False)
    mobile = Column(String, nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=False)
    pan_number = Column(String, nullable=False, unique=True)
    aadhaar_number = Column(String, nullable=False, unique=True)

    # Employment & Financial Info
    employment_type = Column(Enum(EmploymentType), nullable=False)
    organization_name = Column(String, nullable=True)

    monthly_income = Column(Numeric(12, 2), nullable=False)
    existing_monthly_obligations = Column(Numeric(12, 2), default=0.0)

    # KYC Status
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)

    address_line_1 = Column(String, nullable=False)
    address_line_2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())