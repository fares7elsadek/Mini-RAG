from fastapi import APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
import os
from helper.config import get_settings , Settings
from controllers import DataController
from controllers import ProjectController
import aiofiles
from models import ResponseSignal

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags=["api_v1"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                     settings: Settings = Depends(get_settings)):


    # validate the file properties
    data_controller = DataController()
    valid, message = data_controller.validate_uploaded_file(file=file)

    if not valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": message
            }
        )

    # save file
    file_path = data_controller.get_unique_file_name(filename=file.filename,project_id=project_id)

    try:
        
        async with aiofiles.open(file_path,"wb") as f:
            while chunk := await file.read(settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        return JSONResponse(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                        ,
                        content={
                            "signal": ResponseSignal.FILE_UPLOADED_FAILED.value
                        }
                    )


    return JSONResponse(
                content={
                    "signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value
                }
            )