# from fastapi import APIRouter, Depends
# from scripts.models.image_model import ImageBuildRequest, ImageRemoveRequest, ImageGithubBuildRequest
# from scripts.constants.api_endpoints import Endpoints
# from scripts.handlers.image_handler import ( build_image, build_image_from_github,
# remove_image, list_images, pull_image, push_image, dockerhub_login)
# from scripts.logging.logger import logger
# from fastapi.security import OAuth2PasswordBearer
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
# image_router = APIRouter()
#
#
# @image_router.post(Endpoints.IMAGE_BUILD_ADVANCED)
# def build_image_service(data: ImageBuildRequest, token: str = Depends(oauth2_scheme)):
#     logger.info(f"User is attempting to build an image with tag: {data.tag}")
#     return build_image(data, token)
#
#
# @image_router.post(Endpoints.IMAGE_BUILD_FROM_GITHUB)
# def build_image_from_github_service(data: ImageGithubBuildRequest, token: str = Depends(oauth2_scheme)):
#     logger.info(f"User is attempting to build an image from GitHub repository: {data.github_url}")
#     return build_image_from_github(data, token)
#
#
# @image_router.get(Endpoints.IMAGE_LIST)
# def list_images_service(name: str = None, all: bool = False, filters: dict = None, token: str = Depends(oauth2_scheme)):
#     logger.info(f"User is listing Docker images with filters: {filters}")
#     return list_images(name, all, filters, token)
#
#
# @image_router.post(Endpoints.DOCKER_REGISTRY_LOGIN)
# def dockerhub_login_service(username: str, password: str, token: str = Depends(oauth2_scheme)):
#     logger.info(f"User is attempting to login to DockerHub with username: {username}")
#     return dockerhub_login(username, password, token)
#
#
# @image_router.post(Endpoints.IMAGE_PUSH)
# def push_image_service(local_tag: str, remote_repo: str, token: str = Depends(oauth2_scheme)):
#     logger.info(f"User is attempting to push image with tag: {local_tag} to remote repository: {remote_repo}")
#     return push_image(local_tag, remote_repo, token)
#
#
# @image_router.post(Endpoints.IMAGE_PULL)
# def pull_image_service(repository: str, local_tag: str = None, token: str = Depends(oauth2_scheme)):
#     logger.info(f"User is attempting to pull image from repository: {repository}")
#     return pull_image(repository, local_tag, token)
#
#
# @image_router.delete(Endpoints.IMAGE_DELETE)
# def remove_image_service(image_name: str, params: ImageRemoveRequest, token: str = Depends(oauth2_scheme)):
#     logger.info(f"User is attempting to remove image with name: {image_name}")
#     return remove_image(image_name, params, token)



from fastapi import APIRouter, Depends
from scripts.constants.api_endpoints import Endpoints
from scripts.models.image_model import ImageBuildRequest, ImageRemoveRequest, ImageGithubBuildRequest
from scripts.handlers.image_handler import (
    build_image,
    build_image_from_github,
    remove_image,
    list_images,
    pull_image,
    push_image,
    dockerhub_login
)
from scripts.utils.jwt_utils import get_current_user_from_token
from scripts.models.jwt_model import TokenData

image_router = APIRouter()

@image_router.post(Endpoints.IMAGE_BUILD_ADVANCED.replace("/images", ""))
def build_image_route(data: ImageBuildRequest, current_user: TokenData = Depends(get_current_user_from_token)):
    return build_image(data, current_user)

@image_router.post(Endpoints.IMAGE_BUILD_FROM_GITHUB.replace("/images", ""))
def github_build_route(data: ImageGithubBuildRequest, current_user: TokenData = Depends(get_current_user_from_token)):
    return build_image_from_github(data, current_user)

@image_router.get(Endpoints.IMAGE_LIST.replace("/images", ""))
def list_images_route(
    name: str = None,
    all: bool = False,
    filters: dict = None,
    current_user: TokenData = Depends(get_current_user_from_token)
):
    return list_images(name, all, filters, current_user)

@image_router.post(Endpoints.IMAGE_PUSH.replace("/images", ""))
def push_image_route(local_tag: str, remote_repo: str, current_user: TokenData = Depends(get_current_user_from_token)):
    return push_image(local_tag, remote_repo, current_user)

@image_router.post(Endpoints.IMAGE_PULL.replace("/images", ""))
def pull_image_route(repository: str, local_tag: str = None, current_user: TokenData = Depends(get_current_user_from_token)):
    return pull_image(repository, local_tag, current_user)

@image_router.delete(Endpoints.IMAGE_DELETE.replace("/images", ""))
def remove_image_route(image_name: str, params: ImageRemoveRequest, current_user: TokenData = Depends(get_current_user_from_token)):
    return remove_image(image_name, params, current_user)

@image_router.post(Endpoints.DOCKER_REGISTRY_LOGIN.replace("/images", ""))
def dockerhub_login_route(username: str, password: str, current_user: TokenData = Depends(get_current_user_from_token)):
    return dockerhub_login(username, password, current_user)
