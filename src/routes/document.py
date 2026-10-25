import logging
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Query,Request
from fastapi.encoders import jsonable_encoder
from core.dependencies import get_document_model, get_datachunk_model
from core.exceptions import NotFoundException,AppException
from models import ResponseSignal
from models import DocumentModel,DataChunkModel
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from controllers import DataController


logger = logging.getLogger(__name__)

document_router = APIRouter(
    prefix="/api/v1/document",
    tags=["Documents"],
)


def serialize(data):
    return jsonable_encoder(
        data,
        custom_encoder={ObjectId: str},
    )

@document_router.get("")
async def get_document(
    document_id: Annotated[str, Query(...)],
    controller: DocumentModel = Depends(get_document_model),
):
    document = await controller.get_document(document_id=document_id)

    if document is None:
        raise NotFoundException("Document", document_id)

    return serialize({"document": document})


@document_router.get("/all")
async def get_all_documents(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    controller: DocumentModel = Depends(get_document_model),
):
    documents, total_pages = await controller.get_all_documents(
        page=page,
        size=size,
    )

    return serialize({
        "documents": documents,
        "pages": total_pages,
    })


@document_router.delete("")
async def delete_document(
    request: Request,
    document_id: Annotated[str, Query(...)],
    document_model: DocumentModel = Depends(get_document_model),
    datachunk_model: DataChunkModel = Depends(get_datachunk_model)
):

    document = await document_model.get_document(document_id=document_id)
    if document is None:
        raise NotFoundException("Document", document_id)


    client: AsyncIOMotorClient = request.app.state.mongo_client
    async def transaction(session):
        no_chunks = await datachunk_model.delete_chunks_by_document_id(document_id=document_id,session=session)
        deleted = await document_model.delete_document(document_id=document_id,session=session)
        return deleted, no_chunks

    try:

        async with await client.start_session() as session:
            deleted, no_chunks = await session.with_transaction(
                transaction
            )

        
        if not deleted:
            raise NotFoundException("Document", document_id)

       
        document_deleted = DataController._remove_file(document.document_path)
        if not document_deleted:
            logger.exception("Document not deleted (%s)", document.document_path)

        return {
            "signal": ResponseSignal.DOCUMENT_DELETION_SUCCESS.value,
            "deleted": True,
            "no_chunks": no_chunks
        }
    
    except PyMongoError:
        logger.exception("Transaction failed while deleting document %s", document_id)
        raise AppException(
            status_code=500,
            message=ResponseSignal.PROJECT_DELETION_FAILED.value
        )
    
    

    


@document_router.get("/project/{project_id}")
async def get_document_by_projectId(
    project_id: str,
    controller: DocumentModel = Depends(get_document_model),
):
    documents = await controller.get_documents_by_project(project_id=project_id)

    return serialize({"documents": documents})