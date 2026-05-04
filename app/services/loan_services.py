from decimal import Decimal
import random

from app.utils.emi import calculate_emi, calculate_foir
from app.services.underwriting import evaluate_loan
from app.models.user_profile_model import UserProfile
from app.enums.loan_enums import INTEREST_RATES, LoanStatus,InterestRateType


def process_loan_logic(loan, db):
    # Fetch user profile (for DOB)
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == loan.user_id
    ).first()

    if not profile:
        raise Exception("User profile not found")

    # Mock credit score
    credit_score = random.randint(600, 800)

    #  Interest rate (static for now)
    interest_rate = INTEREST_RATES[loan.loan_type]

    #  EMI
    emi = calculate_emi(
        loan.requested_amount,
        float(interest_rate),
        loan.tenure_months
    )

     #  Adjust based on interest rate type
    if loan.interest_rate_type == InterestRateType.FIXED:
        interest_rate = interest_rate
    else:
        # simple floating logic (mock)
        interest_rate = interest_rate + Decimal("0.5")

    #  FOIR
    obligations = loan.existing_monthly_obligations or Decimal("0")
    income = loan.monthly_income

    foir = calculate_foir(income, obligations, emi)

    # Underwriting
    result = evaluate_loan(
        loan.loan_type,
        credit_score,
        foir,
        loan.requested_amount
    )

    #  Save results
    loan.credit_score = credit_score
    loan.foir = foir
    loan.emi = emi
    loan.interest_rate = interest_rate

    if result.approved:
        loan.status = LoanStatus.APPROVED
        loan.approved_amount = result.approved_amount
    else:
        loan.status = LoanStatus.REJECTED
        loan.rejection_reason = result.reason