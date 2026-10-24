import logging
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, StringConstraints
from motor.motor_asyncio import AsyncIOMotorDatabase

from controllers import ProjectController
from models import ResponseSignal

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


def get_controller(request: Request) -> ProjectController:
    db_client: AsyncIOMotorDatabase = request.app.state.mongodb
    return ProjectController(db_client=db_client)



@project_router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    request: Request,
    payload: CreateProjectRequest,
):
    try:
        controller = get_controller(request)

        project = await controller.create_project(
            project_name=payload.project_name
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Project creation failed.",
            )

        return serialize({
            "signal": ResponseSignal.PROJECT_CREATION_SUCCESS.value,
            "project": project,
        })

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create project")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the project.",
        )



@project_router.get("")
async def get_project(
    request: Request,
    project_id: Annotated[int, Query(gt=0)],
):
    try:
        controller = get_controller(request)

        project = await controller.get_project(
            project_id=project_id
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        return serialize({"project": project})

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to retrieve project")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the project.",
        )



@project_router.get("/all")
async def get_all_projects(
    request: Request,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
):
    try:
        controller = get_controller(request)

        projects, total_pages = await controller.get_all_projects(
            page=page,
            size=size,
        )

        return serialize({
            "projects": projects,
            "pages": total_pages,
        })

    except Exception:
        logger.exception("Failed to retrieve projects")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving projects.",
        )



@project_router.delete("")
async def delete_project(
    request: Request,
    project_id: Annotated[int, Query(gt=0)],
):
    try:
        controller = get_controller(request)

        deleted = await controller.delete_project(
            project_id=project_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        return {
            "signal": ResponseSignal.PROJECT_DELETION_SUCCESS.value
            if hasattr(ResponseSignal, "PROJECT_DELETION_SUCCESS")
            else "project_deletion_success",
            "deleted": True,
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to delete project")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the project.",
        )