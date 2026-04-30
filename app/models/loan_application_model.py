from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text, Numeric
from sqlalchemy.sql import func
from app.database import Base
from app.enums.loan_enums import LoanType, InterestRateType, LoanStatus,EmploymentType


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # --- Standard Info ---
    full_name = Column(String, nullable=False)
    mobile = Column(String, nullable=False)

    loan_type = Column(Enum(LoanType), nullable=False)
    requested_amount = Column(Numeric(12, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    interest_rate_type = Column(Enum(InterestRateType), nullable=False)

    # --- Financial Snapshot ---
    monthly_income = Column(Numeric(12, 2), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False)
    organization_name = Column(String, nullable=True)
    existing_monthly_obligations = Column(Numeric(12, 2), default=0)

    # --- VEHICLE LOAN ---
    vehicle_make = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    is_used_vehicle = Column(Boolean, default=False)
    vehicle_registration_number = Column(String, nullable=True)

    # --- GOLD LOAN ---
    gold_weight_grams = Column(Numeric(8, 2), nullable=True)
    gold_purity = Column(Integer, nullable=True)  # 22, 24

    # --- BUSINESS LOAN ---
    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    gst_number = Column(String, nullable=True)
    business_vintage_years = Column(Integer, nullable=True)

    # --- HOME LOAN ---
    property_type = Column(String, nullable=True)
    property_address_line_1 = Column(String, nullable=True)
    property_address_line_2 = Column(String, nullable=True)
    property_city = Column(String, nullable=True)
    property_state = Column(String, nullable=True)
    property_pincode = Column(String, nullable=True)
    estimated_property_value = Column(Numeric(15, 2), nullable=True)

    # --- Decision Fields ---
    consent_given = Column(Boolean, nullable=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=False)

    credit_score = Column(Integer, nullable=True)
    foir = Column(Numeric(5, 2), nullable=True)
    approved_amount = Column(Numeric(12, 2), nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    emi = Column(Numeric(10, 2), nullable=True)

    status = Column(Enum(LoanStatus), default=LoanStatus.INITIATED, nullable=False)
    rejection_reason = Column(Text, nullable=True)

    # --- Metadata ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


