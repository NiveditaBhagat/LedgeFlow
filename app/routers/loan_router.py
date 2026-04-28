#API endpoints
from app.database import get_db
from app.core.security import get_current_user
from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.models.user_profile_model import UserProfile,KYCStatus
from app.models.loan_application_model import LoanApplication
from app.models.user_model import UserRole
from app.schemas.loan_schema import LoanApplicationRequest
from starlette import status

router=APIRouter(
    prefix='/loan',
    tags=['loan']
)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.post("/apply",status_code=status.HTTP_201_CREATED)
async def apply_loan( loan_request: LoanApplicationRequest,db: db_dependency,current_user:user_dependency):
    if current_user.role != UserRole.BORROWER:
        raise HTTPException(
            status_code=403,
            detail="Only borrowers can apply for loans"
        )
