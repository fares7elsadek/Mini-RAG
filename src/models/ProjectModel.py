from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)

from .BaseDataModel import BaseDataModel
from models.enums.DataBaseEnum import DataBaseEnum
from .database.project import Project



class ProjectModel(BaseDataModel):

    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)

        self.collection: AsyncIOMotorCollection = (
            self.db_client[DataBaseEnum.PROJECT_COLLECTION.value]
        )

   
    async def create_project(self, project_name: str) -> Project:
        largest_project = await self.collection.find_one(
            sort=[("project_id", -1)]
        )

        next_project_id = (
            largest_project["project_id"] + 1
            if largest_project is not None
            else 1
        )

        project = Project(
            project_name=project_name,
            project_id=next_project_id
        )

        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude={"id"})
        )

        project._id = result.inserted_id

        return project



    async def get_project(self, project_id: int) -> Project | None:
        project = await self.collection.find_one({
            "project_id":project_id
        })

        if project is None:
            return None

        return Project(**project)


    async def delete_project(self, project_id: int) -> bool:
        result = await self.collection.delete_one({
            "project_id":project_id
        })

        return result.deleted_count > 0


    async def get_all_projects(
        self, page: int = 1, size: int = 10
    ) -> tuple[list[Project], int]:

        total_documents = await self.collection.count_documents({})

        total_pages = (total_documents + size - 1) // size

        cursor = (
            self.collection.find()
            .skip((page - 1) * size)
            .limit(size)
        )

        projects: list[Project] = []

        async for document in cursor:
            projects.append(Project(**document))

        return projects, total_pages