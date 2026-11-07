import logging
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Query,Request
from fastapi.encoders import jsonable_encoder
from core.dependencies import get_document_model, get_datachunk_model,get_db
from core.exceptions import NotFoundException,AppException
from models import ResponseSignal
from models import DocumentModel,DataChunkModel
from pymongo.errors import PyMongoError
from controllers import DataController
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)

document_router = APIRouter(
    prefix="/api/v1/document",
    tags=["Documents"],
)



@document_router.get("")
async def get_document(
    document_id: Annotated[int, Query(...)],
    controller: DocumentModel = Depends(get_document_model),
):
    document = await controller.get_document(document_id=document_id)

    if document is None:
        raise NotFoundException("Document", document_id)

    return {"document": document}


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

    return {
        "documents": documents,
        "pages": total_pages,
    }


@document_router.delete("")
async def delete_document(
    document_id: Annotated[int, Query(...)],
    document_model: DocumentModel = Depends(get_document_model),
    datachunk_model: DataChunkModel = Depends(get_datachunk_model),
    db_client: AsyncSession = Depends(get_db)
):

    # 1. Check document existence
    document = await document_model.get_document(
        document_id=document_id
    )

    if document is None:
        raise NotFoundException("Document", document_id)

    try:
        # 2. Execute database operations atomically
        async with db_client.begin():

            # Delete associated chunks first
            no_chunks = await datachunk_model.delete_chunks_by_document_id(
                document_id=document_id
            )

            # Delete document record
            deleted = await document_model.delete_document(
                document_id=document_id
            )

            if not deleted:
                raise NotFoundException("Document", document_id)

        # Transaction committed successfully here.

        # 3. Delete physical file after successful commit
        try:
            document_deleted = DataController._remove_file(
                document.document_path
            )

            if not document_deleted:
                logger.warning(
                    "Document file could not be deleted: %s",
                    document.document_path
                )

        except OSError:
            logger.exception(
                "Failed to delete document file: %s",
                document.document_path
            )

        return {
            "signal": ResponseSignal.DOCUMENT_DELETION_SUCCESS.value,
            "deleted": True,
            "no_chunks": no_chunks
        }

    except NotFoundException:
        raise

    except SQLAlchemyError:
        logger.exception(
            "Transaction failed while deleting document %s",
            document_id
        )

        raise AppException(
            status_code=500,
            message=ResponseSignal.DOCUMENT_DELETION_FAILED.value
        )
    
    

    


@document_router.get("/project/{project_id}")
async def get_document_by_projectId(
    project_id: int,
    controller: DocumentModel = Depends(get_document_model),
):
    documents = await controller.get_documents_by_project(project_id=project_id)

    return {"documents": documents}