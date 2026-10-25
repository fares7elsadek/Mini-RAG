from .BaseDataModel import BaseDataModel
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
    AsyncIOMotorClientSession
)
from models.enums.DataBaseEnum import DataBaseEnum
from models.database.document import Document
from bson import ObjectId
from datetime import datetime, timezone




class DocumentModel(BaseDataModel):

    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.collection: AsyncIOMotorCollection  = self.db_client[DataBaseEnum.DOCUMENT_COLLECTION.value]


    async def create_document(self, document: Document, session: AsyncIOMotorClientSession | None = None) -> Document:

        document_dict = document.model_dump(by_alias=True, exclude_none=True)
        document_dict["document_type"] = document.document_type.value
        result = await self.collection.insert_one(document_dict, session=session)
        document_id = result.inserted_id
        document.id = document_id
        return document

    async def get_document(self, document_id:str, session: AsyncIOMotorClientSession | None = None) -> Document | None:
        if not ObjectId.is_valid(document_id):
            return None
        
        document = await self.collection.find_one({
            "_id":ObjectId(document_id)
        }, session=session)

        if document is None:
            return None

        return Document(**document)


    async def process_document(self, document_id: str, session: AsyncIOMotorClientSession | None = None) -> bool:
        if not ObjectId.is_valid(document_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"is_processed_to_chunks": True , "updated_at": datetime.now(timezone.utc)}},
            session=session
        )

        return result.matched_count > 0

    async def delete_document(self, document_id: str, session: AsyncIOMotorClientSession | None = None) -> bool:
        if not ObjectId.is_valid(document_id):
            return False

        result = await self.collection.delete_one(
            {"_id": ObjectId(document_id)},
            session=session
        )

        return result.deleted_count > 0 

    async def get_documents_by_project(self, project_id: str, session: AsyncIOMotorClientSession | None = None) -> list[Document]:
        if not ObjectId.is_valid(project_id):
            return []

        documents_cursor = self.collection.find(
            {"project_id": ObjectId(project_id)},
            session=session
        )

        documents = []
        async for document in documents_cursor:
            documents.append(Document(**document))

        return documents

    async def get_all_documents(self, page: int = 1, size: int = 10, session: AsyncIOMotorClientSession | None = None) -> tuple[list[Document], int]:
        total_documents = await self.collection.count_documents({}, session=session)

        total_pages = (total_documents + size - 1) // size

        cursor = (
            self.collection.find()
            .skip((page - 1) * size)
            .limit(size)
        )

        documents: list[Document] = []

        async for document in cursor:
            documents.append(Document(**document))

        return documents, total_pages

    async def delete_documents_by_project(self, project_id: str, session: AsyncIOMotorClientSession | None = None) -> int:
        if not ObjectId.is_valid(project_id):
            return 0

        result = await self.collection.delete_many(
            {"project_id": ObjectId(project_id)},
            session=session
        )

        return result.deleted_count