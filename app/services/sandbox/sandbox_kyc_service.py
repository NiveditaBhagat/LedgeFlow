import requests

from app.core.config import (
    SANDBOX_API_KEY,
    SANDBOX_BASE_URL
)

from app.services.sandbox.auth_service import (
    SandboxKYCProvider
)


class SandboxPANService:

    @staticmethod
    def verify_pan(
        pan_number: str,
        full_name: str,
        dob: str
    ):

        access_token = (
            SandboxKYCProvider.get_access_token()
        )

        url = (
            f"{SANDBOX_BASE_URL}/kyc/pan/verify"
        )

        headers = {
            "Authorization": access_token,
            "x-api-key": SANDBOX_API_KEY,
            "x-api-version": "1.0",
            "Content-Type": "application/json"
        }

        payload = {
            "@entity": "in.co.sandbox.kyc.pan_verification.request",
            "pan": pan_number,
            "name_as_per_pan": full_name,
            "date_of_birth": dob,
            "consent": "Y",
            "reason": "For onboarding customers"
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        print(response.status_code)
        print(response.text)

        if response.status_code != 200:
            return response.json()

        return response.json()