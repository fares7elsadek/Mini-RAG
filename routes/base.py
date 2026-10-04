from fastapi import APIRouter
import os

router = APIRouter(
    prefix = "/api/v1",
    tags=["api_v1"]
)

@router.get("/info")
async def info():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")

    return {
        "app_name": app_name,
        "app_version": app_version
    }
