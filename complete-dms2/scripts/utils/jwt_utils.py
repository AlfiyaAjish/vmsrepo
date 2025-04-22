# from datetime import datetime, timedelta
# from typing import Optional
# from jose import jwt, JWTError, ExpiredSignatureError
# from fastapi import HTTPException, Request, status
# from scripts.constants.app_configuration import settings
# from scripts.constants.app_constants import *
# from scripts.models.jwt_model import TokenData
#
# SECRET_KEY = settings.JWT_SECRET
# ALGORITHM = settings.JWT_ALGORITHM
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
#
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
# def decode_access_token(token: str) -> dict:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except ExpiredSignatureError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=TOKEN_EXPIRED)
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN)
#
# def verify_access_token(token: str) -> Optional[TokenData]:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         role: str = payload.get("role")
#
#         if username is None or role is None:
#             raise JWTError("Token missing username or role")
#
#         return TokenData(username=username, role=role)
#
#     except JWTError:
#         return None
#
# def get_current_user_from_token(request: Request) -> TokenData:
#     auth_header: Optional[str] = request.headers.get("Authorization")
#
#     if auth_header and auth_header.lower().startswith("bearer "):
#         token = auth_header.split(" ")[1]
#         token_data = verify_access_token(token)
#
#         if token_data:
#             return token_data
#
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)
#
# def create_user_token(username: str, role: str) -> str:
#     payload = {
#         "sub": username,
#         "role": role,
#     }
#     return create_access_token(payload)
#
# def decode_user_token(token: str) -> TokenData:
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         return TokenData(**payload)
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials"
#         )
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, ExpiredSignatureError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from scripts.constants.app_configuration import settings
from scripts.constants.app_constants import *
from scripts.models.jwt_model import TokenData
from scripts.utils.mongo_utils import MongoDBConnection

# Token URL must match the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
mongodb = MongoDBConnection()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(username: str) -> Optional[dict]:
    user = mongodb.get_collection("users").find_one({"username": username})
    if user:
        return {
            "username": user["username"],
            "hashed_password": user["password"],
            "role": user.get("role", "user")
        }
    return None

def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return TokenData(username=username, role=role)
    except (JWTError, ExpiredSignatureError):
        raise credentials_exception
