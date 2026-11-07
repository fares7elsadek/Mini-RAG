import logging
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorClient

from controllers import ProjectController, DataController
from core.dependencies import get_project_controller,get_document_model,get_datachunk_model, get_project_model,get_db
from core.exceptions import NotFoundException, AppException
from models import ResponseSignal
from models import ProjectModel,DocumentModel, DataChunkModel
from models.schemas.schemas import ProjectCreate,ProjectResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)

project_router = APIRouter(
    prefix="/api/v1/project",
    tags=["Projects"],
)


@project_router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    controller: ProjectController = Depends(get_project_controller),
):
    project = await controller.create_project(
        project=payload
    )

    if project is None:
        raise NotFoundException("Project", payload.project_name)

    return {
        "signal": ResponseSignal.PROJECT_CREATION_SUCCESS.value,
        "project": project,
    }


@project_router.get("")
async def get_project(
    project_id: Annotated[int, Query(gt=0)],
    controller: ProjectController = Depends(get_project_controller),
):
    project = await controller.get_project(project_id=project_id)

    if project is None:
        raise NotFoundException("Project", project_id)

    return {"project": project}


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

    return {
        "projects": projects,
        "pages": total_pages,
    }


@project_router.delete("")
async def delete_project(
    project_id: int,
    project_model: ProjectModel = Depends(get_project_model),
    document_model: DocumentModel = Depends(get_document_model),
    datachunk_model: DataChunkModel = Depends(get_datachunk_model),
    db_client: AsyncSession = Depends(get_db)
):

    try:
        async with db_client.begin():

            # Get documents before deleting them
            documents = await document_model.get_documents_by_project(
                project_id=project_id
            )

            # 1. Delete chunks first (foreign key dependency)
            no_chunks = await datachunk_model.delete_chunks_by_project_id(
                project_id=project_id
            )

            # 2. Delete documents
            no_documents = await document_model.delete_documents_by_project(
                project_id=project_id
            )

            # 3. Delete project
            deleted = await project_model.delete_project(
                project_id=project_id
            )

            if not deleted:
                raise NotFoundException("Project", project_id)

        

        # 4. Delete physical files AFTER commit
        for document in documents:
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
            "signal": ResponseSignal.PROJECT_DELETION_SUCCESS.value,
            "deleted": True,
            "no_documents": no_documents,
            "no_chunks": no_chunks
        }

    except NotFoundException:
        raise

    except SQLAlchemyError:
        logger.exception(
            "Database transaction failed while deleting project %s",
            project_id
        )

        raise AppException(
            status_code=500,
            message=ResponseSignal.PROJECT_DELETION_FAILED.value
        )

    

    