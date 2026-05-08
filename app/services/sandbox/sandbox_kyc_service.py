

def mock_verify_pan(pan_number: str):
    """
    Mock KYC logic:
    - PAN starting with 'A' → VALID
    - Else → INVALID
    """

    if pan_number.startswith("D"):
        return {
            "status": "VALID",
            "message": "PAN verified successfully (mock)"
        }
    else:
        return {
            "status": "INVALID",
            "message": "PAN verification failed (mock)"
        }