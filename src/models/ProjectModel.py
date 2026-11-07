from .BaseDataModel import BaseDataModel
from models.schemas.schemas import ProjectCreate, ProjectResponse
from models.database.project import Project
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete,update,func
import math


class ProjectModel(BaseDataModel):

    def __init__(self, db_client: AsyncSession):
        super().__init__(db_client)

   
    async def create_project(self, project: ProjectCreate) -> ProjectResponse:
        new_project = Project(**project.model_dump())

        self.db_client.add(new_project)

        await self.db_client.flush()
        await self.db_client.refresh(new_project)

        return ProjectResponse.model_validate(new_project)



    async def get_project(self, project_id: int) -> ProjectResponse | None:
        stmt = select(Project).where(Project.id == project_id)

        result = await self.db_client.execute(stmt)

        project = result.scalar_one_or_none()

        if project is None:
            return None

        return ProjectResponse.model_validate(project)


    async def delete_project(self, project_id: int) -> bool:
        stmt = delete(Project).where(Project.id == project_id)

        result = await self.db_client.execute(stmt)
        
        return result.rowcount > 0


    async def get_all_projects(
        self, page: int = 1, size: int = 10,
    ) -> tuple[list[ProjectResponse], int]:

        if page < 1 or size < 1:
            raise ValueError("Page and size must be greater than zero")

        count_stmt = select(func.count()).select_from(Project)

        total_projects = await self.db_client.scalar(count_stmt)

        # 2. Calculate total pages
        total_pages = math.ceil(total_projects / size) if total_projects else 0

        # 3. Fetch paginated documents
        offset = (page - 1) * size

        stmt = (
             select(Project)
            .order_by(Project.updated_at.desc())
            .offset(offset)
            .limit(size)
        )

        result = await self.db_client.execute(stmt)

        projects = result.scalars().all()

        # 4. Convert ORM objects to Pydantic schemas
        response = [
            ProjectResponse.model_validate(project)
            for project in projects
        ]

        return response, total_pages
    
    async def index_project(self, project_id: int):
        stmt = (
             update(Project)
            .where(Project.id == project_id)
            .values(is_indexed=True,updated_at= datetime.now(UTC))
        )
        
        result = await self.db_client.execute(stmt)

        return result.rowcount > 0