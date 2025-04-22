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

from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordBearer

from scripts.constants.app_configuration import settings
from scripts.constants.app_constants import *
from scripts.models.jwt_model import TokenData

# OAuth2 scheme to be used globally in routers and OpenAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT configuration from settings
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# --- Create Access Token ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Create Token For User ---
def create_user_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
    }
    return create_access_token(payload)

# --- Decode Access Token To Username Only ---
def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing username"
            )

        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# --- Decode Access Token To User Info (username + role) ---
def decode_user_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing username or role"
            )

        return {
            "username": username,
            "role": role
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# --- Verify Token (used in Depends) ---
def verify_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role is None:
            raise JWTError("Token missing username or role")

        return TokenData(username=username, role=role)

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=TOKEN_EXPIRED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN)

# --- Dependency Injection for FastAPI Routers ---
def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    token_data = verify_access_token(token)

    if token_data:
        return token_data

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)
