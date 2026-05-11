import pytest

from app.main import app
from tests.conftest import client, TestingSessionLocal

from app.models.user_profile_model import UserProfile
from app.models.user_model import UserRole

from app.core.security import get_current_user


# python -m pytest tests/test_user_profile.py -v
# python -m pytest tests/test_loan_router.py -v 


# -------- FAKE USER --------
class FakeUser:
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role


# -------- DEFAULT OVERRIDE --------
def override_get_current_user():
    return FakeUser(
        id=1,
        email="test@test.com",
        role=UserRole.BORROWER
    )


app.dependency_overrides[get_current_user] = override_get_current_user


# ---------------- TEST DATA ----------------
create_payload = {
    "full_name": "Test User",
    "mobile": "9876543210",
    "date_of_birth": "1998-01-01",
    "pan_number": "ABCDE1234F",
    "aadhaar_number": "123456789012",
    "employment_type": "SALARIED",
    "organization_name": "Infosys",
    "monthly_income": "50000",
    "existing_monthly_obligations": "5000",
    "address_line_1": "Street 1",
    "city": "Jaipur",
    "state": "Rajasthan",
    "pincode": "302017"
}


# ---------------- CLEANUP FIXTURE ----------------
from app.models.user_model import User  # Ensure you import your User model

@pytest.fixture(autouse=True)
def setup_and_cleanup_db():
    db = TestingSessionLocal()

    # 1. CLEANUP: Clear both tables to ensure a fresh state
    db.query(UserProfile).delete(synchronize_session=False)
    db.query(User).delete(synchronize_session=False)
    db.commit()

    # 2. SEED: Create the users that your FakeUser objects refer to
    test_user_1 = User(id=1, email="test@test.com", role=UserRole.BORROWER, hashed_password="...")
    test_user_2 = User(id=2, email="lender@test.com", role=UserRole.BORROWER, hashed_password="...")
    
    db.add(test_user_1)
    db.add(test_user_2)
    db.commit()

    yield

    # 3. TEARDOWN: Clean up after the test
    db.query(UserProfile).delete(synchronize_session=False)
    db.query(User).delete(synchronize_session=False)
    db.commit()
    db.close()


# ---------------- CREATE ----------------
def test_create_user_profile():

    response = client.post(
        "/user_profile/",
        json=create_payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test User"
    assert data["mobile"] == "9876543210"
    assert data["kyc_status"] == "PENDING"


# ---------------- GET ----------------
def test_get_user_profile():

    client.post(
        "/user_profile/",
        json=create_payload
    )

    response = client.get(
        "/user_profile/get_user_profile"
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Test User"


# ---------------- UPDATE ----------------
def test_update_user_profile():

    client.post(
        "/user_profile/",
        json=create_payload
    )

    response = client.patch(
        "/user_profile/update",
        json={
            "full_name": "Updated Name",
            "mobile": "9999999999",
            "date_of_birth": "1998-01-01",
            "address_line_1": "Street 2",
            "city": "Jaipur",
            "state": "Rajasthan",
            "pincode": "302017"
        }
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


# ---------------- DUPLICATE PROFILE ----------------
def test_duplicate_profile():

    client.post(
        "/user_profile/",
        json=create_payload
    )

    response = client.post(
        "/user_profile/",
        json=create_payload
    )

    assert response.status_code == 400


# ---------------- ROLE RESTRICTION ----------------
def test_role_restriction():

    def override_lender():
        return FakeUser(
            id=2,
            email="lender@test.com",
            role=UserRole.CREDIT
        )

    # override with restricted role
    app.dependency_overrides[get_current_user] = override_lender

    response = client.post(
        "/user_profile/",
        json=create_payload
    )

    assert response.status_code == 403

    # reset override
    app.dependency_overrides[get_current_user] = override_get_current_user