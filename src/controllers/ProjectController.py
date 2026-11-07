import logging
import os

from .BaseController import BaseController
from models import ProjectModel
from sqlalchemy.ext.asyncio import AsyncSession
from models.database.project import Project
from models.schemas.schemas import ProjectCreate,ProjectResponse

logger = logging.getLogger(__name__)


class ProjectController(BaseController):

    def __init__(self, db_client: AsyncSession):
        super().__init__()
        self.project_model = ProjectModel(db_client=db_client)

    @staticmethod
    def get_project_path(project_id: str) -> str:
        project_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "files",
            project_id,
        )

        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    async def create_project(self, project: ProjectCreate) -> ProjectResponse:
        return await self.project_model.create_project(
            project=project
        )

    async def get_project(self, project_id: int) -> ProjectResponse | None:
        return await self.project_model.get_project(
            project_id=project_id,
        )

    async def delete_project(self, project_id: int) -> bool:
        return await self.project_model.delete_project(
            project_id=project_id,
        )

    async def get_all_projects(
        self, page: int = 1, size: int = 10,
    ) -> tuple[list[ProjectResponse], int]:
        return await self.project_model.get_all_projects(
            page=page,
            size=size,
        )
