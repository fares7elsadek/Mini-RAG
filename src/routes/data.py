import logging

from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import aiofiles

from helper.config import get_settings, Settings
from controllers import DataController, ProcessController
from core.dependencies import get_project_controller, get_document_model, get_datachunk_model
from core.exceptions import NotFoundException, ValidationException, AppException
from controllers import ProjectController
from models import ResponseSignal, DataChunkModel, DocumentModel
from .schemas.data import ProcessRequest
from models.database import Document, DataChunk
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: int,
    file: UploadFile,
    settings: Settings = Depends(get_settings),
    project_controller: ProjectController = Depends(get_project_controller),
    document_model: DocumentModel = Depends(get_document_model)
):
    # check project existence
    project = await project_controller.get_project(project_id=project_id)
    if project is None:
        raise NotFoundException("Project", project_id)

    # validate the file properties
    data_controller = DataController()
    valid, message = data_controller.validate_uploaded_file(file=file)
    if not valid:
        raise ValidationException(message)

    # save file
    file_path, file_id = data_controller.get_unique_file_name(
        filename=file.filename,
        project_id=str(project.project_id),
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except OSError:
        logger.exception("Failed to write file to disk: %s", file_path)
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=ResponseSignal.FILE_UPLOADED_FAILED.value,
        )

    process_controller = ProcessController(project_id=str(project.project_id))

    document = Document(
        project_id=project.id,
        document_name=file_id,
        document_path=file_path,
        document_type=process_controller.get_file_type(file_id=file_id),
        document_size=process_controller.get_file_size(file_path=file_path),
        uploaded_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    result_document = await document_model.create_document(document=document)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
            "document": jsonable_encoder(result_document),
        },
    )


@data_router.post("/process/{project_id}")
async def process_data(
    request: Request,
    project_id: int,
    process_request: ProcessRequest,
    project_controller: ProjectController = Depends(get_project_controller),
    document_model: DocumentModel = Depends(get_document_model),
    datachunk_model: DataChunkModel = Depends(get_datachunk_model),
):
    # check project existence
    project = await project_controller.get_project(project_id=project_id)
    if project is None:
        raise NotFoundException("Project", project_id)

    file_id = process_request.file_id
    document = await document_model.get_document(document_id=file_id)
    if document is None:
        raise NotFoundException("Document", file_id)

    if document.is_processed_to_chunks:
        raise ValidationException("Document has already been processed into chunks.")

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_obj = ProcessController(project_id=str(project.project_id))
    content = process_obj.get_file_content(file=document)
    file_chunks = process_obj.process_file_content(
        file_content=content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap=overlap_size,
    )

    if file_chunks is None or len(file_chunks) == 0:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=ResponseSignal.FILE_PROCESSING_FAILED.value,
        )

    chunks: list[DataChunk] = [
        DataChunk(
            chunk_document_id=document.id,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id,
            chunk_txt=chunk.page_content,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    client = request.app.state.mongo_client

    async def transaction(session: AsyncIOMotorClientSession):
        no_records = await datachunk_model.insert_many_chunks(
            chunks=chunks,
            session=session,
        )

        await document_model.process_document(
            document_id=document.id,
            session=session,
        )

        return no_records

    try:
        async with await client.start_session() as session:
            no_records = await session.with_transaction(
                transaction
            )

        if no_records > 0:
            deleted = DataController._remove_file(document.document_path)
            if not deleted:
                logger.exception("Document not deleted (%s)", document.document_path)

        return {
            "signal": ResponseSignal.FILE_PROCESSING_SUCCESSFUL.value,
            "number_of_chunks": no_records,
        }

    except PyMongoError:
        logger.exception("Transaction failed while processing document %s", file_id)
        raise AppException(
            status_code=500,
            message=ResponseSignal.FILE_PROCESSING_FAILED.value
        )

    
