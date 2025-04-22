# from fastapi import APIRouter, status, Depends
# from scripts.constants.api_endpoints import Endpoints
# from scripts.handlers.rate_limit_handler import (
#     get_rate_limit_handler,
#     set_rate_limit_handler,
#     update_rate_limit_handler
# )
# from scripts.models.rate_limit_model import RateLimitConfig
# from scripts.logging.logger import logger
#
# rate_limit_router = APIRouter()
#
# @rate_limit_router.get(Endpoints.RATE_LIMIT_GET, response_model=RateLimitConfig)
# def get_rate_limit_view(user_id: str):
#     logger.info(f"Getting rate limit for user '{user_id}'")
#     return get_rate_limit_handler(user_id)
#
# @rate_limit_router.post(Endpoints.RATE_LIMIT_SET, status_code=status.HTTP_201_CREATED)
# def set_rate_limit_view(user_id: str, limit: int, time_window: int):
#     logger.info(f"Setting rate limit for user '{user_id}' to {limit} with time window of {time_window}")
#     return set_rate_limit_handler(user_id, limit, time_window)
#
# @rate_limit_router.put(Endpoints.RATE_LIMIT_UPDATE)
# def update_rate_limit_view(user_id: str, limit: int, time_window: int):
#     logger.info(f"Updating rate limit for user '{user_id}' to {limit} with time window of {time_window}")
#     return update_rate_limit_handler(user_id, limit, time_window)


from fastapi import APIRouter, status, Depends
from scripts.constants.api_endpoints import Endpoints
from scripts.handlers.rate_limit_handler import (
    get_rate_limit_handler,
    set_rate_limit_handler,
    update_rate_limit_handler
)
from scripts.models.rate_limit_model import RateLimitConfig
from scripts.logging.logger import logger
from scripts.utils.jwt_utils import get_current_user_from_token
from scripts.models.jwt_model import TokenData

rate_limit_router = APIRouter()

@rate_limit_router.get(Endpoints.RATE_LIMIT_GET, response_model=RateLimitConfig)
def get_rate_limit_view(user_id: str, current_user: TokenData = Depends(get_current_user_from_token)):
    logger.info(f"Getting rate limit for user '{user_id}'")
    return get_rate_limit_handler(user_id, current_user)

@rate_limit_router.post(Endpoints.RATE_LIMIT_SET, status_code=status.HTTP_201_CREATED)
def set_rate_limit_view(user_id: str, limit: int, time_window: int, current_user: TokenData = Depends(get_current_user_from_token)):
    logger.info(f"Setting rate limit for user '{user_id}'")
    return set_rate_limit_handler(user_id, limit, time_window, current_user)

@rate_limit_router.put(Endpoints.RATE_LIMIT_UPDATE)
def update_rate_limit_view(user_id: str, limit: int, time_window: int, current_user: TokenData = Depends(get_current_user_from_token)):
    logger.info(f"Updating rate limit for user '{user_id}'")
    return update_rate_limit_handler(user_id, limit, time_window, current_user)
