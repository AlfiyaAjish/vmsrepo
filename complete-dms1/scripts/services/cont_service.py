# from fastapi import APIRouter, Query, Body, Depends, HTTPException
# from scripts.handlers.cont_handler import *
# from scripts.models.cont_model import *
# from scripts.constants.api_endpoints import Endpoints
# from scripts.logging.logger import logger
# from scripts.utils.jwt_utils import get_current_user_from_token
# from fastapi.security import OAuth2PasswordBearer
# from typing import Optional
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")
#
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = get_current_user_from_token(token)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return user
#
# container_router = APIRouter()
#
# @container_router.post(Endpoints.CONTAINER_CREATE)
# def run_container_view(
#     request: ContainerRunAdvancedRequest,
#     user: dict = Depends(get_current_user)
# ):
#     logger.info(f"User '{user['username']}' running container with basic parameters")
#     return run_container_advanced(request, token=user['access_token'])
#
# @container_router.post(Endpoints.CONTAINER_CREATE_ADVANCED)
# def run_container_advanced_view(
#     data: ContainerRunAdvancedRequest,
#     user: dict = Depends(get_current_user)
# ):
#     logger.info(f"User '{user['username']}' running container with advanced parameters")
#     return run_container_advanced(data, token=user['access_token'])
#
# @container_router.post(Endpoints.CONTAINER_LIST)
# def list_containers_view(
#     params: ContainerListRequest = Body(...),
#     user: dict = Depends(get_current_user)  # Get the full user object
# ):
#     logger.info(f"User '{user['username']}' listing containers with filters: {params.dict(exclude_unset=True)}")
#     return list_containers_with_filters(params, token=user['access_token'])
#
# @container_router.post(Endpoints.CONTAINER_LOGS)
# def get_container_logs(
#     name: str,
#     params: ContainerLogsRequest = Body(...),
#     user: dict = Depends(get_current_user)
# ):
#     logger.info(f"User '{user['username']}' fetching logs for container '{name}' with params: {params.dict(exclude_unset=True)}")
#     return get_logs_with_params(name, params, token=user['access_token'])
#
# @container_router.post(Endpoints.CONTAINER_STOP)
# def stop_container_view(
#     name: str,
#     timeout: Optional[float] = Query(None, description="Timeout in seconds before force stop"),
#     user: dict = Depends(get_current_user)
# ):
#     logger.info(f"User '{user['username']}' stopping container '{name}' with timeout={timeout}")
#     return stop_container(name, timeout, token=user['access_token'])
#
# @container_router.post(Endpoints.CONTAINER_START)
# def start_container_view(
#     name: str,
#     user: dict = Depends(get_current_user)
# ):
#     logger.info(f"User '{user['username']}' starting container '{name}'")
#     return start_container(name, token=user['access_token'])
#
# @container_router.post(Endpoints.CONTAINER_DELETE)
# def remove_container_view(
#     name: str,
#     params: ContainerRemoveRequest = Body(...),
#     user: dict = Depends(get_current_user)
# ):
#     logger.info(f"User '{user['username']}' removing container '{name}' with params: {params.dict(exclude_unset=True)}")
#     return remove_container_with_params(name, params, token=user['access_token'])
from fastapi import APIRouter, Query, Body, Depends
from typing import Optional
from scripts.constants.api_endpoints import Endpoints
from scripts.handlers.cont_handler import *
from scripts.models.cont_model import *
from scripts.utils.jwt_utils import get_current_user_from_token
from scripts.models.jwt_model import TokenData

container_router = APIRouter()

@container_router.post(Endpoints.CONTAINER_CREATE.replace("/container", ""))
def run_container_route(request: ContainerRunAdvancedRequest, current_user: TokenData = Depends(get_current_user_from_token)):
    return run_container_advanced(request, current_user)

@container_router.post(Endpoints.CONTAINER_CREATE_ADVANCED.replace("/container", ""))
def run_advanced_container_route(data: ContainerRunAdvancedRequest, current_user: TokenData = Depends(get_current_user_from_token)):
    return run_container_advanced(data, current_user)

@container_router.post(Endpoints.CONTAINER_LOGS.replace("/container", ""))
def container_logs_route(name: str, params: ContainerLogsRequest = Body(...), current_user: TokenData = Depends(get_current_user_from_token)):
    return get_logs_with_params(name, params, current_user)

@container_router.post(Endpoints.CONTAINER_STOP.replace("/container", ""))
def stop_container_route(name: str, timeout: Optional[float] = Query(None), current_user: TokenData = Depends(get_current_user_from_token)):
    return stop_container(name, timeout, current_user)

@container_router.post(Endpoints.CONTAINER_START.replace("/container", ""))
def start_container_route(name: str, current_user: TokenData = Depends(get_current_user_from_token)):
    return start_container(name, current_user)

@container_router.post(Endpoints.CONTAINER_DELETE.replace("/container", ""))
def remove_container_route(name: str, params: ContainerRemoveRequest = Body(...), current_user: TokenData = Depends(get_current_user_from_token)):
    return remove_container_with_params(name, params, current_user)

@container_router.post(Endpoints.CONTAINER_LIST.replace("/container", ""))
def list_containers_route(params: ContainerListRequest = Body(...), current_user: TokenData = Depends(get_current_user_from_token)):
    return list_containers_with_filters(params, current_user)
