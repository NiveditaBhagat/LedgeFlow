from enum import Enum

from app.enums.loan_enums import LoanType
from app.models.user_model import UserRole

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


DOCUMENT_REVIEW_ACCESS = {

    DocumentType.PAN: [
        UserRole.ADMIN,
        UserRole.OPS
    ],

    DocumentType.AADHAR: [
        UserRole.ADMIN,
        UserRole.OPS
    ],

    DocumentType.SALARY_SLIP: [
        UserRole.ADMIN,
        UserRole.CREDIT
    ],

    DocumentType.BANK_STATEMENT: [
        UserRole.ADMIN,
        UserRole.CREDIT
    ],

    DocumentType.PROPERTY_DOC: [
        UserRole.ADMIN,
        UserRole.CREDIT,
        UserRole.OPS
    ],

    DocumentType.VEHICLE_RC: [
        UserRole.ADMIN,
        UserRole.OPS
    ]
}


REQUIRED_DOCS = {
    LoanType.PERSONAL: [
        DocumentType.SALARY_SLIP,
        DocumentType.BANK_STATEMENT
    ],

    LoanType.HOME: [
        DocumentType.PROPERTY_DOC,
        DocumentType.BANK_STATEMENT,
        DocumentType.SALARY_SLIP
    ],

    LoanType.VEHICLE: [
        DocumentType.VEHICLE_RC,
        DocumentType.BANK_STATEMENT
    ]
}