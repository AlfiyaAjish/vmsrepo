# import docker
# from docker.errors import NotFound
# from fastapi import HTTPException, Depends
# from fastapi.security import OAuth2PasswordBearer
# from scripts.utils.mongo_utils import MongoDBConnection
# from scripts.models.cont_model import (
#     ContainerRunAdvancedRequest,
#     ContainerListRequest,
#     ContainerLogsRequest,
#     ContainerLogsResponse,
#     ContainerRemoveRequest
# )
# from scripts.constants.app_constants import (
#     CONTAINER_CREATE_FAILURE,
#     CONTAINER_START_SUCCESS,
#     CONTAINER_STOP_SUCCESS,
#     CONTAINER_LIST_FAILURE,
#     CONTAINER_STOP_FAILURE,
#     CONTAINER_START_FAILURE,
#     CONTAINER_LOGS_FAILURE,
#     CONTAINER_LOGS_RETRIEVED,
#     CONTAINER_REMOVE_FAILURE,
#     CONTAINER_REMOVE_SUCCESS,
#     CONTAINER_NOT_FOUND
# )
# from scripts.utils.jwt_utils import get_current_user_from_token
# from datetime import datetime
# from scripts.utils.rate_limit_utils import check_rate_limit
#
#
# client = docker.from_env()
# mongo = MongoDBConnection()
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
# def run_container_advanced(data: ContainerRunAdvancedRequest, token: str = Depends(oauth2_scheme)):
#     try:
#         kwargs = data.dict(exclude_unset=True)
#         image = kwargs.pop("image")
#         command = kwargs.pop("command", None)
#
#         user = get_current_user_from_token(token)
#         user_id = user.id
#
#         check_rate_limit(user_id)
#
#         container = client.containers.run(image=image, command=command, **kwargs)
#
#         containers_collection = mongo.get_collection("user_containers")
#         containers_collection.insert_one({
#             "user_id": user_id,
#             "container_name": container.name,
#             "created_time": datetime.utcnow()
#         })
#
#         return {
#             "message": CONTAINER_START_SUCCESS,
#             "id": container.id,
#             "status": container.status
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=CONTAINER_CREATE_FAILURE)
#
#
# def list_containers_with_filters(params: ContainerListRequest, token: str = Depends(oauth2_scheme)):
#     try:
#         kwargs = params.dict(exclude_unset=True)
#
#         user = get_current_user_from_token(token)
#
#         if user.role != "Admin":
#             raise HTTPException(status_code=403, detail="You do not have permission to access all containers.")
#
#         containers = client.containers.list(**kwargs)
#
#         return [
#             {
#                 "name": c.name,
#                 "id": c.id,
#                 "image": c.image.tags,
#                 "status": c.status
#             } for c in containers
#         ]
#     except Exception:
#         raise HTTPException(status_code=500, detail=CONTAINER_LIST_FAILURE)
#
#
# def stop_container(name: str, timeout: float = None, token: str = Depends(oauth2_scheme)):
#     try:
#         container = client.containers.get(name)
#         stop_args = {"timeout": timeout} if timeout is not None else {}
#
#         user = get_current_user_from_token(token)
#
#         if user.role != "Admin":
#             raise HTTPException(status_code=403, detail="You do not have permission to stop containers.")
#
#         container.stop(**stop_args)
#         return {"message": CONTAINER_STOP_SUCCESS}
#     except NotFound:
#         raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
#     except Exception:
#         raise HTTPException(status_code=500, detail=CONTAINER_STOP_FAILURE)
#
#
# def start_container(name: str, token: str = Depends(oauth2_scheme)):
#     try:
#         container = client.containers.get(name)
#
#         user = get_current_user_from_token(token)
#
#         if user.role != "Admin":
#             raise HTTPException(status_code=403, detail="You do not have permission to start containers.")
#
#         container.start()
#         return {"message": CONTAINER_START_SUCCESS}
#     except NotFound:
#         raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
#     except Exception:
#         raise HTTPException(status_code=500, detail=CONTAINER_START_FAILURE)
#
#
# def get_logs_with_params(name: str, params: ContainerLogsRequest, token: str = Depends(oauth2_scheme)) -> ContainerLogsResponse:
#     try:
#         container = client.containers.get(name)
#         opts = params.dict(exclude_unset=True)
#
#         user = get_current_user_from_token(token)
#
#         if opts.pop("follow", False):
#             raise HTTPException(status_code=400, detail="Streaming logs not supported in structured response.")
#
#         raw_logs = container.logs(stream=False, **opts)
#         logs = raw_logs.decode("utf-8", errors="ignore").splitlines()
#
#         return ContainerLogsResponse(
#             container_id=name,
#             logs=logs,
#             message=CONTAINER_LOGS_RETRIEVED
#         )
#
#     except NotFound:
#         raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{CONTAINER_LOGS_FAILURE}: {str(e)}")
#
#
# def remove_container_with_params(name: str, params: ContainerRemoveRequest, token: str = Depends(oauth2_scheme)):
#     try:
#         container = client.containers.get(name)
#         opts = params.dict(exclude_unset=True)
#
#         user = get_current_user_from_token(token)
#
#         if user.role != "Admin":
#             raise HTTPException(status_code=403, detail="You do not have permission to remove containers.")
#
#         container.remove(**opts)
#         return {
#             "message": CONTAINER_REMOVE_SUCCESS,
#             "used_options": opts
#         }
#     except NotFound:
#         raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
#     except Exception:
#         raise HTTPException(status_code=500, detail=CONTAINER_REMOVE_FAILURE)



import docker
from fastapi import HTTPException
from datetime import datetime
from scripts.utils.mongo_utils import MongoDBConnection
from scripts.models.cont_model import *
from scripts.constants.app_constants import *
from scripts.utils.rate_limit_utils import check_rate_limit
from scripts.models.jwt_model import TokenData

client = docker.from_env()
mongo = MongoDBConnection()

def run_container_advanced(data: ContainerRunAdvancedRequest, current_user: TokenData):
    check_rate_limit(current_user.username)
    kwargs = data.dict(exclude_unset=True)
    image = kwargs.pop("image")
    command = kwargs.pop("command", None)
    container = client.containers.run(image=image, command=command, **kwargs)
    mongo.get_collection("user_containers").insert_one({
        "user_id": current_user.username,
        "container_name": container.name,
        "created_time": datetime.utcnow()
    })
    return {"message": CONTAINER_START_SUCCESS, "id": container.id, "status": container.status}

def list_containers_with_filters(params: ContainerListRequest, current_user: TokenData):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admin only.")
    containers = client.containers.list(**params.dict(exclude_unset=True))
    return [{"name": c.name, "id": c.id, "image": c.image.tags, "status": c.status} for c in containers]

def get_logs_with_params(name: str, params: ContainerLogsRequest, current_user: TokenData):
    container = client.containers.get(name)
    if params.follow:
        raise HTTPException(status_code=400, detail="Streaming not supported")
    logs = container.logs(**params.dict(exclude_unset=True)).decode("utf-8").splitlines()
    return ContainerLogsResponse(container_id=name, logs=logs, message=CONTAINER_LOGS_RETRIEVED)

def stop_container(name: str, timeout: float, current_user: TokenData):
    container = client.containers.get(name)
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Only admin can stop containers")
    container.stop(timeout=timeout)
    return {"message": CONTAINER_STOP_SUCCESS}

def start_container(name: str, current_user: TokenData):
    container = client.containers.get(name)
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Only admin can start containers")
    container.start()
    return {"message": CONTAINER_START_SUCCESS}

def remove_container_with_params(name: str, params: ContainerRemoveRequest, current_user: TokenData):
    container = client.containers.get(name)
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Only admin can remove containers")
    container.remove(**params.dict(exclude_unset=True))
    return {"message": CONTAINER_REMOVE_SUCCESS}
