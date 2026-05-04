#STP Decision Logic
#This file houses  Business Rule Engine (BRE)
#Eligibility Checks: It runs math like the FOIR (Fixed Obligation to Income Ratio) or LTV (Loan to Value) to see if the borrower can afford the loan.
#Hard Rejections: It instantly rejects applications that don't meet minimum criteria (e.g., "If Age < 21" or "If CIBIL < 700").
#Risk Scoring: It assigns a "score" to the borrower based on the data they provided.
#Automatic Sanctioning: If the borrower passes every rule perfectly, the code updates the loan status to APPROVED and triggers the next step (like generating a Sanction Letter)


from dataclasses import dataclass
from decimal import Decimal
from app.enums.loan_enums import LOAN_RULES


@dataclass
class UnderwritingResult:
    approved: bool
    reason: str | None
    approved_amount: Decimal | None



def evaluate_loan(loan_type, credit_score, foir, requested_amount):
    rules = LOAN_RULES.get(loan_type)

    if credit_score < rules["min_credit_score"]:
        return UnderwritingResult(False, "Low credit score", None)

    if rules["max_foir"] is not None and foir > rules["max_foir"]:
        return UnderwritingResult(False, "High FOIR", None)

    return UnderwritingResult(True, None, requested_amount)