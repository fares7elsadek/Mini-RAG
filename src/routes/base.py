from fastapi import APIRouter,Depends
import os
from helper.config import get_settings

base_router = APIRouter(
    prefix = "/api/v1",
    tags=["api_v1"]
)

@base_router.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    settings = get_settings()

    app_name = settings.APP_NAME
    app_version = settings.APP_VERSION
    file_extensions = settings.FILE_ALLOWED_EXTENSIONS
    allowed_size = settings.FILE_MAX_SIZE_IN_MB

    return {
        "app_name": app_name,
        "app_version": app_version,
        "file_extensions": file_extensions,
        "allowed_size": allowed_size
    }
