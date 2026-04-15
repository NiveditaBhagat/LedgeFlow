from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException 
from app.database import get_db
from starlette import status
from app.core.security import authenticate_user, bcrypt_context, create_access_token
from app.models.user_model import User
from app.schemas import auth_schema


router=APIRouter(
    prefix='/auth',
    tags=['auth']
)


db_dependency=Annotated[Session,Depends(get_db)]


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: auth_schema.UserCreate):
    existing_user=db.query(User).filter(User.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pass=bcrypt_context.hash(create_user_request.password)

    create_user_model=User(
        email=create_user_request.email,
        hashed_password=hashed_pass,
        role=create_user_request.role
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return {"message": "User created successfully"}



@router.post("/token",response_model=auth_schema.Token)
async def login_for_access_token(db: db_dependency,login_request: auth_schema.UserLogin):
    user=authenticate_user(login_request.email,login_request.password,db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token=create_access_token(user.email,user.id,user.role,timedelta(minutes=60))
    return{'access_token':token,'token_type':'bearer'}
