from fastapi import APIRouter, Depends
from helper.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


@base_router.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "file_extensions": settings.FILE_ALLOWED_EXTENSIONS,
        "allowed_size": settings.FILE_MAX_SIZE_IN_MB,
    }
