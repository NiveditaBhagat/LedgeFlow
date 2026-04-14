# JWT logic (Token generation and Password hashing)

from passlib.context import CryptContext
from passlib.context import CryptContext
from app.core.config import SECRET_KEY
from datetime import datetime, timedelta, timezone
from jose import jwt


bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


#incomplete
def create_access_token(username: str,  user_id: int,role: str, expires_delta: timedelta):
    encode={'sub': username, 'id': user_id,'role':role}
    expires=datetime.now(timezone.utc)+expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)