import enum


class EmploymentType(str, enum.Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    
class LoanType(str, enum.Enum):
    PERSONAL = "PERSONAL"
    HOME = "HOME"
    VEHICLE = "VEHICLE"
    GOLD = "GOLD"
    BUSINESS = "BUSINESS"


class InterestRateType(str, enum.Enum):
    FIXED = "FIXED"
    FLOATING = "FLOATING"


class LoanStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISBURSED = "DISBURSED"



LOAN_RULES = {
    LoanType.PERSONAL: {
        "min_credit_score": 650,
        "max_foir": 50,
    },
    LoanType.HOME: {
        "min_credit_score": 700,
        "max_foir": 45,
    },
    LoanType.BUSINESS: {
        "min_credit_score": 680,
        "max_foir": 55,
    },
    LoanType.VEHICLE: {
        "min_credit_score": 640,
        "max_foir": 50,
    },
    LoanType.GOLD: {
        "min_credit_score": 600,
        "max_foir": None,  # not required
    },
}