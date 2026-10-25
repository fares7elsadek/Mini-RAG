import logging
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, StringConstraints
from motor.motor_asyncio import AsyncIOMotorClient

from controllers import ProjectController, DataController
from core.dependencies import get_project_controller,get_document_model,get_datachunk_model, get_project_model
from core.exceptions import NotFoundException, AppException
from models import ResponseSignal
from models import ProjectModel,DocumentModel, DataChunkModel
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

project_router = APIRouter(
    prefix="/api/v1/project",
    tags=["Projects"],
)


ProjectName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=100,
    ),
]


class CreateProjectRequest(BaseModel):
    project_name: ProjectName


def serialize(data):
    return jsonable_encoder(
        data,
        custom_encoder={ObjectId: str},
    )


@project_router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: CreateProjectRequest,
    controller: ProjectController = Depends(get_project_controller),
):
    project = await controller.create_project(
        project_name=payload.project_name,
    )

    if project is None:
        raise NotFoundException("Project", payload.project_name)

    return serialize({
        "signal": ResponseSignal.PROJECT_CREATION_SUCCESS.value,
        "project": project,
    })


@project_router.get("")
async def get_project(
    project_id: Annotated[int, Query(gt=0)],
    controller: ProjectController = Depends(get_project_controller),
):
    project = await controller.get_project(project_id=project_id)

    if project is None:
        raise NotFoundException("Project", project_id)

    return serialize({"project": project})


@project_router.get("/all")
async def get_all_projects(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    controller: ProjectController = Depends(get_project_controller),
):
    projects, total_pages = await controller.get_all_projects(
        page=page,
        size=size,
    )

    return serialize({
        "projects": projects,
        "pages": total_pages,
    })


@project_router.delete("")
async def delete_project(
    request: Request,
    project_id: str,
    project_model:  ProjectModel = Depends(get_project_model),
    document_model: DocumentModel = Depends(get_document_model),
    datachunk_model: DataChunkModel = Depends(get_datachunk_model),
):
    
    documents = await document_model.get_documents_by_project(project_id=project_id)
    client: AsyncIOMotorClient = request.app.state.mongo_client
    async def transaction(session):
        # Delete all documents associated with the project
        no_documents = await document_model.delete_documents_by_project(project_id=project_id, session=session)
        # Delete all data chunks associated with the project
        no_chunks = await datachunk_model.delete_chunks_by_project_id(project_id=project_id, session=session)
        # Delete the project itself
        deleted = await project_model.delete_project(project_id=project_id, session=session)

        return deleted , no_documents , no_chunks
    
    try:

        async with await client.start_session() as session:
            deleted , no_documents , no_chunks = await session.with_transaction(
                transaction
            )
            

        if not deleted:
            raise NotFoundException("Project", project_id)


        for document in documents:
            document_deleted = DataController._remove_file(document.document_path)
            if not document_deleted:
                logger.exception("Document not deleted (%s)", document.document_path)


        return {
                "signal": ResponseSignal.PROJECT_DELETION_SUCCESS.value,
                "deleted": True,
                "no_documents": no_documents,
                "no_chunks" : no_chunks
            }

    except PyMongoError:
            logger.exception("Transaction failed while deleting project %s", project_id)
            raise AppException(
                status_code=500,
                message=ResponseSignal.PROJECT_DELETION_FAILED.value
            )

    

    