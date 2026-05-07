from datetime import datetime
from decimal import Decimal
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_serializer

from app.models.loan_repayment_model import EMIStatus



IST = ZoneInfo("Asia/Kolkata")

class LoanRepaymentScheduleResponse(BaseModel):

    id: int
    loan_id: int

    installment_number: int

    due_date: datetime

    emi_amount: Decimal
    principal_component: Decimal
    interest_component: Decimal

    remaining_principal: Decimal

    status: EMIStatus

    paid_at: Optional[datetime]

    created_at: datetime

    @field_serializer(
        "due_date",
        "paid_at",
        "created_at"
    )
    def convert_to_ist(self, value: datetime):

        if value is None:
            return value

        return value.astimezone(IST)

    class Config:
        from_attributes = True