import logging
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, StringConstraints
from motor.motor_asyncio import AsyncIOMotorDatabase

from controllers import ProjectController
from core.dependencies import get_project_controller
from core.exceptions import NotFoundException
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
    project_id: Annotated[int, Query(gt=0)],
    controller: ProjectController = Depends(get_project_controller),
):
    deleted = await controller.delete_project(project_id=project_id)

    if not deleted:
        raise NotFoundException("Project", project_id)

    return {
        "signal": ResponseSignal.PROJECT_DELETION_SUCCESS.value,
        "deleted": True,
    }