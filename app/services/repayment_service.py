from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from app.models.loan_repayment_model import (
    LoanRepaymentSchedule,
    EMIStatus
)
from app.utils.emi import calculate_emi


def generate_repayment_schedule(loan, db):

    p = Decimal(str(loan.approved_amount))

    r = (
        Decimal(str(loan.interest_rate))
        / Decimal("100")
        / Decimal("12")
    )

    n = loan.tenure_months

    start_date = datetime.utcnow()

    # EMI Formula
    emi = calculate_emi(
    principal=p,
    annual_rate=float(loan.interest_rate),
    tenure_months=n
)

    current_balance = p

    for i in range(1, n + 1):

        interest_payment = (
            current_balance * r
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        principal_payment = (
            emi - interest_payment
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # Last EMI adjustment
        if i == n:
            principal_payment = current_balance

            emi = (
                principal_payment + interest_payment
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            current_balance = Decimal("0.00")

        else:
            current_balance -= principal_payment

        installment = LoanRepaymentSchedule(
            loan_id=loan.id,

            installment_number=i,

            due_date=start_date + relativedelta(months=i),

            emi_amount=emi,

            principal_component=principal_payment,

            interest_component=interest_payment,

            remaining_principal=max(
                Decimal("0.00"),
                current_balance
            ),

            status=EMIStatus.PENDING
        )

        db.add(installment)

    return emi







def mark_overdue_emis(db):

    now = datetime.now(timezone.utc)

    overdue_emis = db.query(
        LoanRepaymentSchedule
    ).filter(
        LoanRepaymentSchedule.due_date < now,
        LoanRepaymentSchedule.status == EMIStatus.PENDING
    ).all()

    for emi in overdue_emis:
        emi.status = EMIStatus.OVERDUE

    return len(overdue_emis)