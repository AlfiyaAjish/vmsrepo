from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from scripts.services.image_service import image_router
from scripts.services.cont_service import container_router
from scripts.services.vol_service import volume_router
from scripts.services.admin_service import admin_router
from scripts.services.rate_limit_service import rate_limit_router
from scripts.services.jwt_service import auth_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Docker Management API",
        description="APIs to manage Docker Images, Containers, and Volumes",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with clean prefixes
    app.include_router(auth_router, prefix="/auth", tags=["Authentication Operations"])
    app.include_router(admin_router, prefix="/admin", tags=["Admin Operations"])
    app.include_router(rate_limit_router, prefix="/rate-limit", tags=["Rate Limit Operations"])
    app.include_router(image_router, prefix="/images", tags=["Image Operations"])
    app.include_router(container_router, prefix="/container", tags=["Container Operations"])
    app.include_router(volume_router, prefix="/volume", tags=["Volume Operations"])

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }

        for path in openapi_schema["paths"].values():
            for method in path.values():
                method.setdefault("security", [{"BearerAuth": []}])

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app
