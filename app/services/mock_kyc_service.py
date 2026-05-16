
class MockKYCProvider:
    @staticmethod
   
    def verify_pan(
        pan_number: str,
        full_name: str,
        dob: str
    ):

        

        if pan_number.startswith("D"):

            return {
                "code": 200,
                "data": {
                    "@entity": "in.co.sandbox.kyc.pan_verification.response",
                    "pan": pan_number,
                    "category": "individual",
                    "status": "valid",
                    "remarks": None,
                    "name_as_per_pan_match": True,
                    "date_of_birth_match": True,
                    "aadhaar_seeding_status": "y"
                }
            }
        
        return {
            "code": 400,
            "data": {
                "@entity": "in.co.sandbox.kyc.pan_verification.response",
                "pan": pan_number,
                "category": "individual",
                "status": "invalid",
                "remarks": "Mock PAN verification failed",
                "name_as_per_pan_match": False,
                "date_of_birth_match": False,
                "aadhaar_seeding_status": "n"
            }
        }

