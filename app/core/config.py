# Environment variables (DB URL, JWT Secret Key)


from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

SANDBOX_API_KEY= os.getenv("SANDBOX_API_KEY")
SANDBOX_API_SECRET=os.getenv("SANDBOX_API_SECRET")
SANDBOX_BASE_URL= os.getenv("SANDBOX_BASE_URL")
