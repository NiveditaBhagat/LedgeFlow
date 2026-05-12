from enum import Enum

class DocumentType(str, Enum):
    PAN = "PAN"
    AADHAR = "AADHAR"
    SALARY_SLIP = "SALARY_SLIP"
    BANK_STATEMENT = "BANK_STATEMENT"
    PROPERTY_DOC = "PROPERTY_DOC"
    VEHICLE_RC = "VEHICLE_RC"


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"