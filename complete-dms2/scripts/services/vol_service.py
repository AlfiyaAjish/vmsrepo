# from fastapi import APIRouter, status, Depends
# from scripts.constants.api_endpoints import Endpoints
# from scripts.handlers.vol_handler import (
#     create_volume_with_params,
#     remove_volume_with_params
# )
# from scripts.models.volume_model import VolumeCreateRequest, VolumeRemoveRequest
# from scripts.logging.logger import logger
#
# volume_router = APIRouter()
#
#
# @volume_router.post(Endpoints.VOLUME_CREATE, status_code=status.HTTP_201_CREATED)
# def create_volume_view(data: VolumeCreateRequest, current_user: dict = Depends(create_volume_with_params)):
#
#     logger.info(f"Request to create volume with data: {data}")
#     return create_volume_with_params(data, current_user)
#
#
# @volume_router.delete(Endpoints.VOLUME_DELETE, status_code=status.HTTP_200_OK)
# def remove_volume_view(name: str, params: VolumeRemoveRequest, current_user: dict = Depends(remove_volume_with_params)):
#
#     logger.info(f"Request to remove volume '{name}' with parameters: {params}")
#     return remove_volume_with_params(name, params, current_user)


from fastapi import APIRouter, status, Depends
from scripts.constants.api_endpoints import Endpoints
from scripts.handlers.vol_handler import (
    create_volume_with_params,
    remove_volume_with_params
)
from scripts.models.volume_model import VolumeCreateRequest, VolumeRemoveRequest
from scripts.logging.logger import logger
from scripts.utils.jwt_utils import get_current_user_from_token
from scripts.models.jwt_model import TokenData

volume_router = APIRouter()

@volume_router.post(Endpoints.VOLUME_CREATE, status_code=status.HTTP_201_CREATED)
def create_volume_view(
    data: VolumeCreateRequest,
    current_user: TokenData = Depends(get_current_user_from_token)
):
    logger.info(f"User '{current_user.username}' creating volume")
    return create_volume_with_params(data, current_user)

@volume_router.delete(Endpoints.VOLUME_DELETE, status_code=status.HTTP_200_OK)
def remove_volume_view(
    volume_name: str,
    params: VolumeRemoveRequest,
    current_user: TokenData = Depends(get_current_user_from_token)
):
    logger.info(f"User '{current_user.username}' removing volume '{volume_name}'")
    return remove_volume_with_params(volume_name, params, current_user)
