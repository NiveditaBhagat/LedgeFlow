# JWT logic (Token generation and Password hashing)

from typing import Annotated

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from passlib.context import CryptContext
from app.core.config import SECRET_KEY
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.models.user_model import User
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from sqlalchemy.orm import Session


bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def authenticate_user(email:str,password:str,db):
    user=db.query(User).filter(User.email==email).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user



def create_access_token(email: str,  user_id: int,role: str, expires_delta: timedelta):
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role
    }
    expire=datetime.now(timezone.utc)+expires_delta
    to_encode.update({'exp':expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


#This will:
#take token from request
#decode it
#give us logged-in user
async def get_current_user(token: Annotated[str,Depends(oauth2_scheme)],db: Session = Depends(get_db)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user=db.query(User).filter(User.id==int(user_id)).first()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
