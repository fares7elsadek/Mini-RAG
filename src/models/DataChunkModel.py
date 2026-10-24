from .BaseDataModel import BaseDataModel
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from models.enums.DataBaseEnum import DataBaseEnum
from models.database.data_chunk import DataChunk
from bson import ObjectId
from pymongo import InsertOne



class DataChunkModel(BaseDataModel):

    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.collection: AsyncIOMotorCollection  = self.db_client[DataBaseEnum.CHUNK_COLLECTION.value]


    async def create_single_chunk(self, chunk: DataChunk) -> DataChunk:
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True,exclude_none=True))
        chunk_id = result.inserted_id
        chunk._id = chunk_id
        return chunk

    async def get_chunk(self, chunk_id:str) -> DataChunk | None:
        chunk = await self.collection.find_one({
            "_id":ObjectId(chunk_id)
        })

        if chunk is None:
            return None

        return DataChunk(**chunk)


    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 100 ) -> int:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True,exclude_none=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)