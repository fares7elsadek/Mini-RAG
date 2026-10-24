from fastapi import APIRouter,Depends,UploadFile,status,Request,HTTPException
from fastapi.responses import JSONResponse
import os
from helper.config import get_settings , Settings
from controllers import DataController,ProcessController
from motor.motor_asyncio import AsyncIOMotorDatabase
from controllers import ProjectController
import aiofiles
from models import ResponseSignal
from .schemas.data import ProcessRequest


data_router = APIRouter(
    prefix = "/api/v1/data",
    tags=["api_v1"]
)


def get_project_controller(request: Request) -> ProjectController:
    db_client: AsyncIOMotorDatabase = request.app.state.mongodb
    return ProjectController(db_client=db_client)



@data_router.post("/upload/{project_id}")
async def upload_data(request: Request,project_id: str, file: UploadFile,
                     settings: Settings = Depends(get_settings)):

    # check project existence
    project_controller = get_project_controller(request=request)
    project = await project_controller.get_project(
                project_id=int(project_id)
            )
    
    if project is None:
                return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "signal": "Project not found"
                            }
                        )

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
    file_path, file_id = data_controller.get_unique_file_name(filename=file.filename,project_id=project_id)

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
                    "signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
                    "file_id": file_id
                }
            )


@data_router.post("/process/{project_id}")
async def process_data(request: Request,project_id: str, process_request: ProcessRequest):

    try:

        # check project existence
        project_controller = get_project_controller(request=request)
        project = await project_controller.get_project(project_id=int(project_id))
        if project is None:
            return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "signal": "Project not found"
                        }
                    )


        file_id = process_request.file_id
        chunk_size = process_request.chunk_size
        overlap_size = process_request.overlap_size

        process_obj = ProcessController(project_id=project_id)
        content = process_obj.get_file_content(file_id=file_id)
        file_chunks = process_obj.process_file_content(file_content=content
                                                    ,file_id=file_id,chunk_size=chunk_size,overlap=overlap_size)
    except Exception as e:
        return JSONResponse(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                                ,
                                content={
                                    "signal": ResponseSignal.FILE_PROCESSING_FAILED.value
                                }
                            )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "signal": ResponseSignal.FILE_PROCESSING_FAILED.value
                    }
                )
    
        
    return file_chunks
