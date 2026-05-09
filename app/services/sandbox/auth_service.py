import requests

from app.core.config import SANDBOX_API_KEY, SANDBOX_API_SECRET, SANDBOX_BASE_URL





class SandboxKYCProvider:

    @staticmethod
    def get_access_token():

        url = f"{SANDBOX_BASE_URL}/authenticate"

        headers = {
            "x-api-key": SANDBOX_API_KEY,
            "x-api-secret": SANDBOX_API_SECRET,
            "x-api-version": "1.0"
        }

        response = requests.post(
            url,
            headers=headers
        )

        print(response.status_code)
        print(response.text)

        response.raise_for_status()

        data = response.json()

        return data["access_token"]