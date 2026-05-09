


from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func,Enum
from enum import Enum as PyEnum
from app.database import Base

class EMIStatus(str, PyEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class LoanRepaymentSchedule(Base):
    __tablename__ = "loan_repayment_schedules"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    
    installment_number = Column(Integer, nullable=False) 
    due_date = Column(DateTime, nullable=False)
    emi_amount = Column(Numeric(12, 2), nullable=False)
    principal_component = Column(Numeric(12, 2), nullable=False)
    interest_component = Column(Numeric(12, 2), nullable=False)
    remaining_principal = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(EMIStatus),
        default=EMIStatus.PENDING) 
    paid_at = Column(DateTime, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
