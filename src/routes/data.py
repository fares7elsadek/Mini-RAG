from fastapi import APIRouter,Depends,UploadFile,status,Request,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import os
from helper.config import get_settings , Settings
from controllers import DataController,ProcessController
from motor.motor_asyncio import AsyncIOMotorDatabase
from controllers import ProjectController
import aiofiles
from models import ResponseSignal, DataChunkModel, DocumentModel
from .schemas.data import ProcessRequest
from models.database import Document,DataChunk



data_router = APIRouter(
    prefix = "/api/v1/data",
    tags=["api_v1"]
)


def get_project_controller(request: Request) -> ProjectController:
    db_client: AsyncIOMotorDatabase = request.app.state.mongodb
    return ProjectController(db_client=db_client)

def get_document_model(request: Request) -> DocumentModel:
    db_client: AsyncIOMotorDatabase = request.app.state.mongodb
    return DocumentModel(db_client=db_client)


def get_datachunk_model(request: Request) -> DataChunkModel:
    db_client: AsyncIOMotorDatabase = request.app.state.mongodb
    return DataChunkModel(db_client=db_client)


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


        document = Document(project_id=project.id,document_name=file_id,document_path=file_path)
        document_model = get_document_model(request=request)

        result_document = await document_model.create_document(document=document)

        return JSONResponse(
                content={
                    "signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
                    "document": jsonable_encoder(result_document)
                }
        )
        
        
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ,
            content={
                "signal": ResponseSignal.FILE_UPLOADED_FAILED.value
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

        document_model = get_document_model(request=request)

        document = await document_model.get_document(document_id=file_id)

        if document is None:
              return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "signal": "Document not found"
                        }
                )

        if document.is_processed_to_chunks:
             return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "signal": "Document already processed"
                        }
                )

        chunk_size = process_request.chunk_size
        overlap_size = process_request.overlap_size

        process_obj = ProcessController(project_id=project_id)
        content = process_obj.get_file_content(file=document)
        file_chunks = process_obj.process_file_content(file_content=content
                                                    ,file_id=file_id,chunk_size=chunk_size,overlap=overlap_size)


        if file_chunks is None or len(file_chunks) == 0:
                return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value
                            }
                        )
        
        
            
                
        datachunk_model = get_datachunk_model(request=request)

        chunks: list[DataChunk] = [
            DataChunk(
                chunk_document_id=document.id,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
                chunk_txt=chunk.page_content
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records = await datachunk_model.insert_many_chunks(chunks=chunks)
        await document_model.process_document(document_id=document.id)

        return JSONResponse(
                status_code=status.HTTP_200_OK
                ,
                content={
                    "signal": ResponseSignal.FILE_PROCESSING_SUCCESSFULL.value,
                    "number_of_chunks": no_records
                }
            )


        
    except Exception as e:

        print(e)
        return JSONResponse(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                                ,
                                content={
                                    "signal": ResponseSignal.FILE_PROCESSING_FAILED.value
                                }
                            )

    
