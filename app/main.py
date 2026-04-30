#uvicorn app.main:app --reload

from fastapi import FastAPI
from app.database import Base
from app.database import engine
from app.models import user_model
from app.routers import auth_router, user_profile_router, kyc_router,loan_router
from app.schemas import loan_schema

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(user_profile_router.router)
app.include_router(kyc_router.router)
app.include_router(loan_router.router)

