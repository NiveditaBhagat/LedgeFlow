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