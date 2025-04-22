# from fastapi import APIRouter, Depends, HTTPException
# from scripts.handlers.jwt_handler import signup_user_handler, login_user_handler, logout_user_handler
# from scripts.models.jwt_model import UserSignupRequest, Token, UserLoginRequest, UserLoginResponse
# from scripts.constants.api_endpoints import Endpoints
# from scripts.logging.logger import logger
# from fastapi.security import OAuth2PasswordBearer
# from scripts.utils.jwt_utils import decode_access_token
#
# auth_router = APIRouter()
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")
#
#
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     username = decode_access_token(token)
#     if not username:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return username
#
#
# @auth_router.post(Endpoints.AUTH_SIGNUP)
# def signup_user(data: UserSignupRequest) -> Token:
#     logger.info(f"User '{data.username}' is signing up with role: {data.role}")
#     return signup_user_handler(data)
#
#
# @auth_router.post(Endpoints.AUTH_LOGIN)
# def login_user(data: UserLoginRequest) -> UserLoginResponse:
#     logger.info(f"User '{data.username}' is attempting to log in.")
#     return login_user_handler(data)
#
#
# @auth_router.post(Endpoints.AUTH_LOGOUT)
# def logout_user(username: str = Depends(get_current_user)):
#     logger.info(f"User '{username}' is logging out.")
#     return logout_user_handler(username)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from scripts.models.jwt_model import TokenData, Token, UserSignupRequest, UserLoginResponse
from scripts.constants.api_endpoints import Endpoints
from scripts.utils.jwt_utils import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user_by_username
)
from scripts.utils.mongo_utils import MongoDBConnection

auth_router = APIRouter()
mongodb = MongoDBConnection()

@auth_router.post(Endpoints.AUTH_SIGNUP, status_code=201)
def signup_user(data: UserSignupRequest) -> Token:
    users_collection = mongodb.get_collection("users")

    if users_collection.find_one({"username": data.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(data.password)

    users_collection.insert_one({
        "username": data.username,
        "password": hashed_password,
        "role": data.role
    })

    access_token = create_access_token({
        "sub": data.username,
        "role": data.role
    })

    return Token(access_token=access_token, token_type="bearer", expires_in=3600)

# ✅ The token endpoint used by Swagger Authorize modal
@auth_router.post("/token", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=60)
    )

    return Token(access_token=access_token, token_type="bearer", expires_in=3600)

@auth_router.post(Endpoints.AUTH_LOGOUT)
def logout_user(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"User '{current_user.username}' logged out successfully"}
