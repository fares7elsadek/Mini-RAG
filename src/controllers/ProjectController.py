
from .BaseController import BaseController
from models import ProjectModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.database.project import Project
import os


class ProjectController(BaseController):

    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__()
        self.project_model = ProjectModel(db_client=db_client)

    @staticmethod
    def get_project_path(project_id: str):
        project_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "files",
            project_id
        )

        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    async def create_project(self, project_name: str) -> Project:
        return await self.project_model.create_project(
            project_name=project_name
        )

    async def get_project(self, project_id: int) -> Project | None:
        return await self.project_model.get_project(
            project_id=project_id
        )

    async def delete_project(self, project_id: int) -> bool:
        return await self.project_model.delete_project(
            project_id=project_id
        )

    async def get_all_projects(
        self, page: int = 1, size: int = 10
    ) -> tuple[list[Project], int]:
        return await self.project_model.get_all_projects(
            page=page,
            size=size
        )
