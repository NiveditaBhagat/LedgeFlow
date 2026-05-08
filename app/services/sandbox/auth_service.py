import requests

from app.core.config import settings


class SandboxKYCProvider:

    @staticmethod
    def get_access_token():

        url = f"{settings.SANDBOX_BASE_URL}/authenticate"

        payload = {
            "apiKey": settings.SANDBOX_API_KEY,
            "apiSecret": settings.SANDBOX_API_SECRET
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise Exception("Sandbox authentication failed")

        data = response.json()

        return data["access_token"]