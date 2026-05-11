from datetime import date

import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

from app.core.config import TEST_DATABASE_URL

from app.models.user_model import User, UserRole
from app.models.loan_application_model import LoanApplication
from app.models.user_profile_model import UserProfile, KYCStatus

from app.enums.loan_enums import EmploymentType, LoanStatus


# TEST DATABASE
engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


# OVERRIDE DB
@pytest.fixture(autouse=True)
def override_db_dependency(db_session):
    def _get_db_override():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.pop(get_db, None)


# app.dependency_overrides[get_db] = override_get_db


# TEST CLIENT
client = TestClient(app)


# CLEAN DB SESSION
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()

    if transaction.is_active:
        transaction.rollback()

    connection.close()


# TEST CLIENT FIXTURE
@pytest.fixture
def test_client():
    return client


# TEST USER
@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password="hashedpassword",
        role=UserRole.BORROWER,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()  # Use flush instead of commit to keep the transaction alive
    db_session.refresh(user)
    return user


# HELPER FUNCTION
def create_valid_loan(user_id, status=LoanStatus.INITIATED):

    return LoanApplication(
        user_id=user_id,
        amount=5000.0,
        status=status,
        interest_rate=0.05
    )