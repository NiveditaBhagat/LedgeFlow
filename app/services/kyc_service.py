from app.core.config import KYC_PROVIDER
from app.services.mock_kyc_service import MockKYCProvider
from app.services.sandbox.auth_service import SandboxKYCProvider
from app.services.sandbox.sandbox_kyc_service import SandboxPANService



class KYCService:

    @staticmethod
    def verify_pan(pan_number: str,
        full_name: str,
        dob: str):

        if KYC_PROVIDER == "sandbox":
            return SandboxPANService.verify_pan(pan_number,full_name,dob)

        return MockKYCProvider.mock_verify_pan(pan_number,full_name,dob)