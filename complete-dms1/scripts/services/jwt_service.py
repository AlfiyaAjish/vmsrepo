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

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from scripts.constants.api_endpoints import Endpoints
from scripts.handlers.jwt_handler import signup_user_handler, login_user_handler, logout_user_handler
from scripts.models.jwt_model import UserSignupRequest

auth_router = APIRouter()

@auth_router.post(Endpoints.AUTH_SIGNUP.replace("/auth", ""), status_code=status.HTTP_201_CREATED)
def signup_user(user: UserSignupRequest):
    return signup_user_handler(user)

@auth_router.post(Endpoints.AUTH_LOGIN.replace("/auth", ""), status_code=status.HTTP_200_OK)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    return login_user_handler(form_data)

@auth_router.post(Endpoints.AUTH_LOGOUT.replace("/auth", ""), status_code=status.HTTP_200_OK)
def logout_user(username: str):
    return logout_user_handler(username)
