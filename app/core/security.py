# JWT logic (Token generation and Password hashing)

from passlib.context import CryptContext
from passlib.context import CryptContext


bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
