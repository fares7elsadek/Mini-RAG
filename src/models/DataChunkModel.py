from .BaseDataModel import BaseDataModel
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
    AsyncIOMotorClientSession
)
from models.enums.DataBaseEnum import DataBaseEnum
from models.database.data_chunk import DataChunk
from bson import ObjectId
from pymongo import InsertOne




class DataChunkModel(BaseDataModel):

    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.collection: AsyncIOMotorCollection  = self.db_client[DataBaseEnum.CHUNK_COLLECTION.value]


    async def create_single_chunk(self, chunk: DataChunk, session: AsyncIOMotorClientSession | None = None) -> DataChunk:
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True,exclude_none=True), session=session)
        chunk_id = result.inserted_id
        chunk._id = chunk_id
        return chunk

    async def get_chunk(self, chunk_id:str, session: AsyncIOMotorClientSession | None = None) -> DataChunk | None:
        chunk = await self.collection.find_one({
            "_id":ObjectId(chunk_id)
        }, session=session)

        if chunk is None:
            return None

        return DataChunk(**chunk)


    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 100, session: AsyncIOMotorClientSession | None = None) -> int:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True,exclude_none=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations, session=session)

        return len(chunks)

    async def get_chunks_by_document_id(self, document_id: str, session: AsyncIOMotorClientSession | None = None) -> list[DataChunk]:
        chunks_cursor = self.collection.find(
            {"chunk_document_id": document_id},
            session=session
        ).sort("chunk_order", 1)

        chunks = []
        async for chunk in chunks_cursor:
            chunks.append(DataChunk(**chunk))

        return chunks

    async def delete_chunks_by_document_id(self, document_id: str, session: AsyncIOMotorClientSession | None = None) -> int:
        result = await self.collection.delete_many(
            {"chunk_document_id": ObjectId(document_id)},
            session=session
        )
        return result.deleted_count

    async def delete_chunks_by_project_id(self, project_id:str, session: AsyncIOMotorClientSession | None = None) -> int:
        result = await self.collection.delete_many(
            {"chunk_project_id": ObjectId(project_id)},
            session=session
        )
        return result.deleted_count