from fastapi import FastAPI
from app.database import Base
from app.database import engine
from app.models import user_model
from app.routers import auth_router
from app.schemas import loan_schema

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)


