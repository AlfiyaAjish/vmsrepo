from fastapi import HTTPException, Request
from scripts.utils.mongo_utils import MongoDBConnection
from scripts.utils.jwt_utils import get_current_user_from_token
from scripts.constants.app_constants import USER_COLLECTION, CONTAINER_COLLECTION, USER_NOT_FOUND
from scripts.logging.logger import logger

mongo = MongoDBConnection()

def list_all_users(request: Request):
    user = get_current_user_from_token(request)

    if user.role != "Admin":
        logger.warning(f"User '{user.username}' attempted to access users list without admin privileges")
        raise HTTPException(status_code=403, detail="You don't have permission to perform this action.")

    try:
        users_collection = mongo.get_collection(USER_COLLECTION)
        users = list(users_collection.find({}, {"_id": 0, "password": 0}))
        logger.info(f"Admin '{user.username}' fetched {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Failed to fetch users: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching users.")


def get_user_details(username: str, request: Request):
    user = get_current_user_from_token(request)

    if user.role != "Admin":
        logger.warning(
            f"User '{user.username}' attempted to access details of user '{username}' without admin privileges")
        raise HTTPException(status_code=403, detail="You don't have permission to perform this action.")

    try:
        users_collection = mongo.get_collection(USER_COLLECTION)
        user_data = users_collection.find_one({"username": username}, {"_id": 0, "password": 0})

        if not user_data:
            logger.warning(f"Admin '{user.username}' could not find user '{username}'")
            raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

        logger.info(f"Admin '{user.username}' fetched details for user '{username}'")
        return user_data
    except Exception as e:
        logger.error(f"Failed to fetch user '{username}': {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching user details.")


def delete_user(username: str, request: Request):
    user = get_current_user_from_token(request)

    if user.role != "Admin":
        logger.warning(f"User '{user.username}' attempted to delete user '{username}' without admin privileges")
        raise HTTPException(status_code=403, detail="You don't have permission to perform this action.")

    try:
        users_collection = mongo.get_collection(USER_COLLECTION)
        result = users_collection.delete_one({"username": username})

        if result.deleted_count == 0:
            logger.warning(f"Admin '{user.username}' tried to delete user '{username}', but not found")
            raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

        logger.info(f"Admin '{user.username}' deleted user '{username}'")
        return {"detail": f"User '{username}' deleted successfully."}
    except Exception as e:
        logger.error(f"Failed to delete user '{username}': {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting user.")


def list_all_containers(request: Request):
    user = get_current_user_from_token(request)

    if user.role != "Admin":
        logger.warning(f"User '{user.username}' attempted to access containers list without admin privileges")
        raise HTTPException(status_code=403, detail="You don't have permission to perform this action.")

    try:
        containers_collection = mongo.get_collection(CONTAINER_COLLECTION)
        containers = list(containers_collection.find({}, {"_id": 0}))
        logger.info(f"Admin '{user.username}' fetched {len(containers)} containers")
        return containers
    except Exception as e:
        logger.error(f"Failed to fetch containers: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching containers.")
