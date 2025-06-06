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
from docker.errors import NotFound
from fastapi import HTTPException
from datetime import datetime

from scripts.utils.mongo_utils import MongoDBConnection
from scripts.utils.rate_limit_utils import check_rate_limit
from scripts.models.jwt_model import TokenData
from scripts.models.cont_model import (
    ContainerRunAdvancedRequest,
    ContainerListRequest,
    ContainerLogsRequest,
    ContainerLogsResponse,
    ContainerRemoveRequest
)
from scripts.constants.app_constants import *

client = docker.from_env()
mongo = MongoDBConnection()

def run_container_advanced(data: ContainerRunAdvancedRequest, user: TokenData):
    try:
        kwargs = data.dict(exclude_unset=True)
        image = kwargs.pop("image")
        command = kwargs.pop("command", None)

        check_rate_limit(user.username)

        container = client.containers.run(image=image, command=command, **kwargs)

        containers_collection = mongo.get_collection("user_containers")
        containers_collection.insert_one({
            "user_id": user.username,
            "container_name": container.name,
            "created_time": datetime.utcnow()
        })

        return {
            "message": CONTAINER_START_SUCCESS,
            "id": container.id,
            "status": container.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{CONTAINER_CREATE_FAILURE}: {str(e)}")

def list_containers_with_filters(params: ContainerListRequest, user: TokenData):
    try:
        kwargs = params.dict(exclude_unset=True)

        if user.role != "Admin":
            raise HTTPException(status_code=403, detail="You do not have permission to access all containers.")

        containers = client.containers.list(**kwargs)

        return [
            {
                "name": c.name,
                "id": c.id,
                "image": c.image.tags,
                "status": c.status
            } for c in containers
        ]
    except Exception:
        raise HTTPException(status_code=500, detail=CONTAINER_LIST_FAILURE)

def stop_container(name: str, timeout: float, user: TokenData):
    try:
        container = client.containers.get(name)

        if user.role != "Admin":
            raise HTTPException(status_code=403, detail="You do not have permission to stop containers.")

        container.stop(timeout=timeout if timeout is not None else 10)
        return {"message": CONTAINER_STOP_SUCCESS}
    except NotFound:
        raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
    except Exception:
        raise HTTPException(status_code=500, detail=CONTAINER_STOP_FAILURE)

def start_container(name: str, user: TokenData):
    try:
        container = client.containers.get(name)

        if user.role != "Admin":
            raise HTTPException(status_code=403, detail="You do not have permission to start containers.")

        container.start()
        return {"message": CONTAINER_START_SUCCESS}
    except NotFound:
        raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
    except Exception:
        raise HTTPException(status_code=500, detail=CONTAINER_START_FAILURE)

def get_logs_with_params(name: str, params: ContainerLogsRequest, user: TokenData) -> ContainerLogsResponse:
    try:
        container = client.containers.get(name)
        opts = params.dict(exclude_unset=True)

        if opts.pop("follow", False):
            raise HTTPException(status_code=400, detail="Streaming logs not supported in this format.")

        raw_logs = container.logs(stream=False, **opts)
        logs = raw_logs.decode("utf-8", errors="ignore").splitlines()

        return ContainerLogsResponse(
            container_id=name,
            logs=logs,
            message=CONTAINER_LOGS_RETRIEVED
        )
    except NotFound:
        raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{CONTAINER_LOGS_FAILURE}: {str(e)}")

def remove_container_with_params(name: str, params: ContainerRemoveRequest, user: TokenData):
    try:
        container = client.containers.get(name)
        opts = params.dict(exclude_unset=True)

        if user.role != "Admin":
            raise HTTPException(status_code=403, detail="You do not have permission to remove containers.")

        container.remove(**opts)
        return {
            "message": CONTAINER_REMOVE_SUCCESS,
            "used_options": opts
        }
    except NotFound:
        raise HTTPException(status_code=404, detail=CONTAINER_NOT_FOUND)
    except Exception:
        raise HTTPException(status_code=500, detail=CONTAINER_REMOVE_FAILURE)
