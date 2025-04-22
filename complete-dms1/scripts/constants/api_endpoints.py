class Endpoints:
    # === Authentication ===
    AUTH_SIGNUP = "/auth/signup"
    AUTH_LOGIN = "/auth/login"
    AUTH_LOGOUT = "/auth/logout"

    # === Rate Limit ===
    RATE_LIMIT_GET = "/rate-limit/{username}"
    RATE_LIMIT_SET = "/rate-limit/{username}/set"
    RATE_LIMIT_UPDATE = "/rate-limit/{username}/update"

    # === Docker Image Operations ===
    IMAGE_BUILD_ADVANCED = "/images/build"
    IMAGE_BUILD_FROM_GITHUB = "/images/github-build"
    DOCKER_REGISTRY_LOGIN = "/images/registry/login"
    IMAGE_PUSH = "/images/push"
    IMAGE_PULL = "/images/pull"
    IMAGE_LIST = "/images"
    IMAGE_DELETE = "/images/{image_name}/delete"

    # === Docker Container Operations ===
    CONTAINER_CREATE = "/container"
    CONTAINER_CREATE_ADVANCED = "/container/advanced"
    CONTAINER_START = "/container/start"
    CONTAINER_STOP = "/container/stop"
    CONTAINER_LOGS = "/container/logs"
    CONTAINER_LIST = "/container/list"
    CONTAINER_DELETE = "/container/delete"

    # === Docker Volume Operations ===
    VOLUME_CREATE = "/volume/create"
    VOLUME_DELETE = "/volume/{volume_name}/delete"

    # === Admin Operations ===
    ADMIN_USERS_LIST = "/admin/users"
    ADMIN_USER_DETAILS = "/admin/users/{username}"
    ADMIN_USER_DELETE = "/admin/users/{username}/delete"
    ADMIN_CONTAINERS_LIST = "/admin/containers"
