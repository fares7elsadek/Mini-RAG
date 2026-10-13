from fastapi import APIRouter,Depends,UploadFile
import os
from helper.config import get_settings

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags=["api_v1"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                     settings: Settings = Depends(get_settings)):


    # validate the file properties