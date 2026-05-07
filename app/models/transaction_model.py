
from decimal import Decimal
import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func,Enum

from app.database import Base


class TransactionType(str, enum.Enum):
    DISBURSEMENT = "DISBURSEMENT"
    REPAYMENT = "REPAYMENT"
    REFUND = "REFUND"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loan_applications.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    bank_id = Column(Integer, ForeignKey("user_bank_details.id"))

    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    reference_id = Column(String, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())