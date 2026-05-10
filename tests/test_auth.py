from tests.conftest import client


# ---------------------------
# 1. Register User Test
# ---------------------------
def test_register_user():
    response = client.post(
        "/auth/",
        json={
            "email": "test_user@test.com",
            "password": "password123",
            "role": "BORROWER"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"


# ---------------------------
# 2. Login Test
# ---------------------------
def test_login():
    email = "login_user@test.com"

    # create user first
    client.post(
        "/auth/",
        json={
            "email": email,
            "password": "password123",
            "role": "BORROWER"
        }
    )

    # login using YOUR API format
    response = client.post(
        "/auth/token",
        json={
            "email": email,
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ---------------------------
# 3. Duplicate Email Test
# ---------------------------
def test_duplicate_email():
    email = "duplicate@test.com"

    # first creation
    client.post(
        "/auth/",
        json={
            "email": email,
            "password": "password123",
            "role": "BORROWER"
        }
    )

    # second creation (should fail)
    response = client.post(
        "/auth/",
        json={
            "email": email,
            "password": "password123",
            "role": "BORROWER"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"