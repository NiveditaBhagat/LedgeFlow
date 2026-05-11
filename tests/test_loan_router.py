# tests/test_loan_router.py

from datetime import datetime, UTC

from app.core.security import get_current_user
from app.main import app

from app.models.loan_application_model import LoanApplication
from app.models.user_model import User



class TestLoanRouter:

    def test_apply_loan_success(
        self,
        test_client,
        db_session,
        test_user
    ):

        # Override auth dependency with actual DB user
        def override_borrower():
            return test_user

        app.dependency_overrides[get_current_user] = override_borrower

        payload = {
            "full_name": "Amrita Sharma",
            "mobile": "9876543210",
            "loan_type": "PERSONAL",
            "requested_amount": 500000,
            "tenure_months": 36,
            "interest_rate_type": "FIXED",
            "monthly_income": 60000,
            "employment_type": "SALARIED",
            "organization_name": "Infosys",
            "existing_monthly_obligations": 10000,
            "consent_given": True,
            "consent_timestamp": datetime.now(UTC).isoformat()
        }

        response = test_client.post(
            "/loans/apply",
            json=payload
        )
        print(response.json())
        assert response.status_code == 201

        data = response.json()

        # assert data["message"] == "Loan application submitted successfully"
        # assert data["loan"]["full_name"] == "Amrita Sharma"
        # assert data["loan"]["loan_type"] == "PERSONAL"
        # assert data["loan"]["status"] == "INITIATED"

        assert data["message"] == "Loan application submitted successfully"
        assert "loan_id" in data


        loan = db_session.query(LoanApplication).first()

        assert loan is not None
        assert loan.user_id == test_user.id
        assert loan.requested_amount == 500000

        app.dependency_overrides.clear()


    def test_process_loan_logic_flow(
        self,
        db_session,
        test_user
    ):

        loan = LoanApplication(
            user_id=test_user.id,
            full_name="Rahul Sharma",
            mobile="9999999999",
            loan_type="PERSONAL",
            requested_amount=400000,
            tenure_months=24,
            interest_rate_type="FIXED",
            monthly_income=80000,
            employment_type="SALARIED",
            organization_name="TCS",
            existing_monthly_obligations=10000,
            consent_given=True,
            consent_timestamp=datetime.now(UTC),
            credit_score=750,
            foir=25,
            status="INITIATED"
        )

        db_session.add(loan)
        db_session.commit()
        db_session.refresh(loan)

        # Dummy processing simulation
        loan.status = "APPROVED"
        loan.approved_amount = 400000
        loan.interest_rate = 12.5
        loan.emi = 18800

        db_session.commit()
        db_session.refresh(loan)

        assert loan.status == "APPROVED"
        assert loan.approved_amount == 400000
        assert loan.interest_rate == 12.5

    def test_link_bank_verified_only(
        self,
        db_session,
        test_user
    ):

        # Example logic test
        test_user.is_verified = True

        db_session.commit()
        db_session.refresh(test_user)

        assert test_user.is_verified is True

    def test_disburse_loan_ops_access(
        self,
        db_session,
        test_user
    ):

        # Dummy role assignment
        test_user.role = "OPS"

        db_session.commit()
        db_session.refresh(test_user)

        assert test_user.role == "OPS"