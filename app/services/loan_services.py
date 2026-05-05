from decimal import Decimal
import random

from fastapi import HTTPException

from app.utils.emi import calculate_emi, calculate_foir
from app.services.underwriting import evaluate_loan
from app.models.user_profile_model import UserProfile
from app.enums.loan_enums import INTEREST_RATES, LoanStatus,InterestRateType, LoanType


def apply_loan_specific_checks(loan):

    def reject(reason: str):
        return False, reason

    # VEHICLE LOAN → only business constraints
    if loan.loan_type == LoanType.VEHICLE:
        if loan.is_used_vehicle:
            if loan.tenure_months > 60:
                return reject("Used vehicle tenure too long")

    # GOLD LOAN → LTV logic
    elif loan.loan_type == LoanType.GOLD:
        GOLD_RATE_PER_GRAM = Decimal("5000")  # mock value
        LTV_RATIO = Decimal("0.75")

        gold_value = loan.gold_weight_grams * GOLD_RATE_PER_GRAM
        max_allowed = gold_value * LTV_RATIO

        if loan.requested_amount > max_allowed:
            return reject("Requested amount exceeds allowed gold LTV")

    # BUSINESS LOAN → financial strength
    elif loan.loan_type == LoanType.BUSINESS:
        if loan.business_vintage_years < 1:
            return reject("Business too new")

        if loan.monthly_income < Decimal("20000"):
            return reject("Income too low for business loan")

    # HOME LOAN → LTV logic
    elif loan.loan_type == LoanType.HOME:
        LTV_RATIO = Decimal("0.80")

        max_allowed = loan.estimated_property_value * LTV_RATIO

        if loan.requested_amount > max_allowed:
            return reject("Requested amount exceeds property LTV")

    # PERSONAL LOAN → basic sanity
    elif loan.loan_type == LoanType.PERSONAL:
        if loan.monthly_income < Decimal("15000"):
            return reject("Income too low")

        if loan.tenure_months > 60:
            return reject("Tenure too long for personal loan")

        if loan.existing_monthly_obligations > loan.monthly_income:
            return reject("Existing obligations too high")

    return True, None


def process_loan_logic(loan, db):

    # validation
    is_valid, reason = apply_loan_specific_checks(loan)

    if not is_valid:
        loan.status = LoanStatus.REJECTED
        loan.rejection_reason = reason

    else:
       
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == loan.user_id
        ).first()

        if not profile:
            raise HTTPException(404, "User profile not found")

        #  credit score
        credit_score = random.randint(600, 800)

        # interest rate
        interest_rate = Decimal(str(INTEREST_RATES[loan.loan_type]))
        if loan.interest_rate_type == InterestRateType.FLOATING:
            interest_rate += Decimal("0.5")

        # EMI
        emi = calculate_emi(
            loan.requested_amount,
            float(interest_rate),
            loan.tenure_months
        )

        #  FOIR
        obligations = loan.existing_monthly_obligations or Decimal("0")
        foir = calculate_foir(loan.monthly_income, obligations, emi)

        #  underwriting
        result = evaluate_loan(
            loan.loan_type,
            credit_score,
            foir,
            loan.requested_amount
        )

        #  save
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

    # SINGLE COMMIT
    db.commit()
    db.refresh(loan)

    return loan