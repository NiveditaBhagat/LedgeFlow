

#API endpoints
from decimal import Decimal
import uuid

from sqlalchemy import Transaction

from app.database import get_db
from app.core.security import get_current_user
from datetime import timedelta, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.models.bank_details_model import UserBankDetails, VerificationStatus
from app.models.loan_repayment_model import EMIStatus, LoanRepaymentSchedule
from app.models.transaction_model import TransactionStatus, TransactionType
from app.models.user_profile_model import UserProfile,KYCStatus
from app.models.loan_application_model import LoanApplication
from app.models.user_model import UserRole
from app.schemas.loan_repayment_schema import LoanRepaymentScheduleResponse
from app.schemas.loan_schema import LoanApplicationRequest,LoanApplyResponse, LoanResponse, LoanSummaryResponse
from starlette import status
from app.enums.loan_enums import  LoanStatus
from datetime import datetime

from app.services.repayment_service import mark_overdue_emis


router=APIRouter(
    prefix='/loan_repayment',
    tags=['loan_repayment']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]




@router.get(
    "/{loan_id}/repayment-schedule",
    response_model=list[LoanRepaymentScheduleResponse]
)
def get_repayment_schedule(
    loan_id: int,
    db: db_dependency,
    current_user: user_dependency
):

    # Fetch loan
    loan = db.query(LoanApplication).filter(
        LoanApplication.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(404, "Loan not found")

   

    # Borrower -> only own loan
    if current_user.role == UserRole.BORROWER:

        if loan.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

    # Internal teams -> global access
    elif current_user.role in [
        UserRole.ADMIN,
        UserRole.CREDIT,
        UserRole.OPS
    ]:
        pass

    # Any other role -> deny
    else:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

   
    # FETCH REPAYMENT SCHEDULE
 

    schedules = db.query(
        LoanRepaymentSchedule
    ).filter(
        LoanRepaymentSchedule.loan_id == loan_id
    ).order_by(
        LoanRepaymentSchedule.installment_number.asc()
    ).all()

    return schedules


@router.post("/repayments/{schedule_id}/pay")
def pay_emi(
    schedule_id: int,
    db: db_dependency,
    current_user: user_dependency
):

    # Only borrower can pay EMI
    if current_user.role != UserRole.BORROWER:
        raise HTTPException(
            status_code=403,
            detail="Only borrower can pay EMI"
        )

    # Fetch EMI schedule
    schedule = db.query(LoanRepaymentSchedule).filter(
        LoanRepaymentSchedule.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Repayment schedule not found"
        )

    # Fetch loan
    loan = db.query(LoanApplication).filter(
        LoanApplication.id == schedule.loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    # Ownership check
    if loan.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    # Already paid
    if schedule.status == EMIStatus.PAID:
        raise HTTPException(
            status_code=400,
            detail="EMI already paid"
        )

    # Create repayment transaction
    txn = Transaction(
        loan_id=loan.id,
        user_id=current_user.id,

        amount=schedule.emi_amount,

        transaction_type=TransactionType.REPAYMENT,

        status=TransactionStatus.SUCCESS,

        reference_id="REPAY_" + str(uuid.uuid4())[:8]
    )

    db.add(txn)

    # Mark EMI paid
    schedule.status = EMIStatus.PAID

    schedule.paid_at = datetime.now(timezone.utc)

    db.commit()

    db.refresh(schedule)

    return {
        "message": "EMI paid successfully",

        "loan_id": loan.id,

        "schedule_id": schedule.id,

        "transaction_reference": txn.reference_id,

        "paid_amount": schedule.emi_amount,

        "status": schedule.status
    }


@router.post("/repayments/mark-overdue")
def mark_overdue(
    db: db_dependency,
    current_user: user_dependency
):

    # Only internal team
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.OPS
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    updated_count = mark_overdue_emis(db)

    db.commit()

    return {
        "message": "Overdue EMI check completed",
        "updated_emis": updated_count
    }



@router.get("/{loan_id}/statement")
def get_loan_statement(
    loan_id: int,
    db: db_dependency,
    current_user: user_dependency
):

    # Fetch loan
    loan = db.query(LoanApplication).filter(
        LoanApplication.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )


    # ACCESS CONTROL
  

    # Borrower -> only own loan
    if current_user.role == UserRole.BORROWER:

        if loan.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

    # Internal team access
    elif current_user.role not in [
        UserRole.ADMIN,
        UserRole.CREDIT,
        UserRole.OPS
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    # FETCH EMI DATA


    schedules = db.query(
        LoanRepaymentSchedule
    ).filter(
        LoanRepaymentSchedule.loan_id == loan.id
    ).all()

    total_emis = len(schedules)

    paid_emis = [
        s for s in schedules
        if s.status == EMIStatus.PAID
    ]

    overdue_emis = [
        s for s in schedules
        if s.status == EMIStatus.OVERDUE
    ]

    pending_emis = [
        s for s in schedules
        if s.status == EMIStatus.PENDING
    ]

 
    # CALCULATIONS

    total_paid = sum(
        Decimal(str(s.emi_amount))
        for s in paid_emis
    )

    total_pending = sum(
        Decimal(str(s.emi_amount))
        for s in pending_emis
    )

    next_emi = None

    if pending_emis:
        next_emi = min(
            pending_emis,
            key=lambda x: x.due_date
        )

    # Remaining principal
    remaining_principal = Decimal("0.00")

    if schedules:
        remaining_principal = schedules[-1].remaining_principal

        for s in schedules:
            if s.status in [
                EMIStatus.PENDING,
                EMIStatus.OVERDUE
            ]:
                remaining_principal = s.remaining_principal
                break


    # RESPONSE
  

    return {

        "loan_id": loan.id,

        "loan_status": loan.status,

        "approved_amount": loan.approved_amount,

        "interest_rate": loan.interest_rate,

        "emi": loan.emi,

        "tenure_months": loan.tenure_months,

        "total_installments": total_emis,

        "paid_installments": len(paid_emis),

        "pending_installments": len(pending_emis),

        "overdue_installments": len(overdue_emis),

        "total_paid_amount": total_paid,

        "total_pending_amount": total_pending,

        "remaining_principal": remaining_principal,

        "next_emi": {
            "installment_number": next_emi.installment_number,
            "due_date": next_emi.due_date,
            "amount": next_emi.emi_amount
        } if next_emi else None
    }