from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import bcrypt

SECRET_KEY = "YOUR_SECRET_KEY"  # Replace with strong secret in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    # encode and truncate if needed
    pw_bytes = password.encode("utf-8")[:72]  # bcrypt limit
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode()

def verify_password(plain_password: str, hashed_password: str):
    pw_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pw_bytes, hashed_password.encode())



def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
