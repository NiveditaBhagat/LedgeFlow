from fastapi import FastAPI
from app.schemas import loan_schema

app = FastAPI()

app.include_router(loan_schema.router)


