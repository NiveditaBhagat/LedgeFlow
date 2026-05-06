import uuid
from rapidfuzz import fuzz  

from app.models.bank_details_model import VerificationStatus


class BankVerificationService:
    MATCH_THRESHOLD = 80  # configurable later

    @staticmethod
    def _normalize(name: str) -> str:
        """
        Normalize names for better matching
        """
        return name.strip().upper()

    @staticmethod
    def verify_account(user_full_name: str, submitted_account_name: str):
        """
        Simulates Penny Drop verification with fuzzy name matching
        """

        # Normalize names
        user_name = BankVerificationService._normalize(user_full_name)
        bank_name = BankVerificationService._normalize(submitted_account_name)

        # Simulated bank response (in real world comes from API)
        bank_returned_name = bank_name

        # Calculate match score (0–100)
        match_score = fuzz.token_sort_ratio(user_name, bank_returned_name)

        # Generate reference ID
        reference_id = uuid.uuid4().hex[:8].upper()

        # Decision
        if match_score >= BankVerificationService.MATCH_THRESHOLD:
            return {
                "status": VerificationStatus.VERIFIED,
                "verified_name": bank_returned_name,
                "reference_id": f"PAY-{reference_id}",
                "score": match_score
            }
        else:
            return {
                "status": VerificationStatus.FAILED,
                "verified_name": bank_returned_name,
                "reference_id": f"ERR-{reference_id}",
                "score": match_score
            }