# import docker
# from fastapi import HTTPException, Depends, status
# from fastapi.security import OAuth2PasswordBearer
# from scripts.models.volume_model import VolumeCreateRequest, VolumeRemoveRequest
# from scripts.constants.app_constants import (
#     VOLUME_CREATE_SUCCESS,
#     VOLUME_CREATE_FAILURE,
#     VOLUME_REMOVE_SUCCESS,
#     VOLUME_REMOVE_FAILURE,
#     VOLUME_NOT_FOUND
# )
# from scripts.utils.jwt_utils import verify_access_token
# from scripts.logging.logger import logger
#
# client = docker.from_env()
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = verify_access_token(token)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
#     return user
#
#
# def create_volume_with_params(data: VolumeCreateRequest, current_user: dict = Depends(get_current_user)):
#     try:
#         if current_user["role"] != "Admin":
#             logger.warning(f"User '{current_user['username']}' is not authorized to create volumes")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You don't have permission to create volumes"
#             )
#
#         opts = data.dict(exclude_unset=True)
#         volume = client.volumes.create(**opts)
#
#         logger.info(f"Created volume '{volume.name}' successfully by user '{current_user['username']}'")
#         return {
#             "message": f"{VOLUME_CREATE_SUCCESS}: '{volume.name}'",
#             "name": volume.name,
#             "driver": volume.attrs.get("Driver"),
#             "labels": volume.attrs.get("Labels")
#         }
#
#     except Exception as e:
#         logger.error(f"Failed to create volume: {str(e)}")
#         raise HTTPException(status_code=500, detail=VOLUME_CREATE_FAILURE)
#
#
# def remove_volume_with_params(name: str, params: VolumeRemoveRequest, current_user: dict = Depends(get_current_user)):
#     try:
#         if current_user["role"] != "Admin":
#             logger.warning(f"User '{current_user['username']}' is not authorized to remove volumes")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You don't have permission to remove volumes"
#             )
#
#         opts = params.dict(exclude_unset=True)
#         volume = client.volumes.get(name)
#         volume.remove(**opts)
#
#         logger.info(f"Removed volume '{name}' successfully by user '{current_user['username']}'")
#         return {"message": f"{VOLUME_REMOVE_SUCCESS}: '{name}'"}
#
#     except docker.errors.NotFound:
#         logger.warning(f"Volume '{name}' not found")
#         raise HTTPException(status_code=404, detail=VOLUME_NOT_FOUND)
#
#     except Exception as e:
#         logger.error(f"Failed to remove volume '{name}': {str(e)}")
#         raise HTTPException(status_code=500, detail=VOLUME_REMOVE_FAILURE)


import docker
from fastapi import HTTPException, status
from scripts.models.volume_model import VolumeCreateRequest, VolumeRemoveRequest
from scripts.constants.app_constants import *
from scripts.logging.logger import logger
from scripts.models.jwt_model import TokenData

client = docker.from_env()

def create_volume_with_params(data: VolumeCreateRequest, current_user: TokenData):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    opts = data.dict(exclude_unset=True)
    volume = client.volumes.create(**opts)
    return {
        "message": f"{VOLUME_CREATE_SUCCESS}: '{volume.name}'",
        "name": volume.name,
        "driver": volume.attrs.get("Driver"),
        "labels": volume.attrs.get("Labels")
    }

def remove_volume_with_params(name: str, params: VolumeRemoveRequest, current_user: TokenData):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    opts = params.dict(exclude_unset=True)
    try:
        volume = client.volumes.get(name)
        volume.remove(**opts)
        return {"message": f"{VOLUME_REMOVE_SUCCESS}: '{name}'"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=VOLUME_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to remove volume: {e}")
        raise HTTPException(status_code=500, detail=VOLUME_REMOVE_FAILURE)
