from .BaseDataModel import BaseDataModel
from models.schemas.schemas import DataChunkCreate,DataChunkResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.database.data_chunk import DataChunk


class DataChunkModel(BaseDataModel):

    def __init__(self, db_client: AsyncSession):
        super().__init__(db_client)

       
    async def create_single_chunk(
        self,
        chunk: DataChunkCreate
    ) -> DataChunkResponse:

        new_chunk = DataChunk(**chunk.model_dump())

        self.db_client.add(new_chunk)

        await self.db_client.flush()
        await self.db_client.refresh(new_chunk)

        return DataChunkResponse.model_validate(new_chunk)

    async def get_chunk(
        self,
        chunk_id: int
    ) -> DataChunkResponse | None:

        stmt = select(DataChunk).where(DataChunk.id == chunk_id)

        result = await self.db_client.execute(stmt)

        chunk = result.scalar_one_or_none()

        if chunk is None:
            return None

        return DataChunkResponse.model_validate(chunk)


    async def insert_many_chunks(self, chunks: list[DataChunkCreate], batch_size: int = 100) -> int:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        if not chunks:
            return 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                DataChunk(**chunk.model_dump())
                for chunk in batch
            ]

            self.db_client.add_all(operations)
            await self.db_client.flush()

        return len(chunks)

    async def get_chunks_by_document_id(
        self,
        document_id: int
    ) -> list[DataChunkResponse]:

        stmt = (
            select(DataChunk)
            .where(DataChunk.chunk_document_id == document_id)
            .order_by(DataChunk.chunk_order)
        )

        result = await self.db_client.execute(stmt)

        chunks = result.scalars().all()

        return [
            DataChunkResponse.model_validate(chunk)
            for chunk in chunks
        ]

    async def delete_chunks_by_document_id(
        self,
        document_id: int
    ) -> int:

        stmt = (
            delete(DataChunk)
            .where(DataChunk.chunk_document_id == document_id)
        )

        result = await self.db_client.execute(stmt)

        return result.rowcount or 0

    async def delete_chunks_by_project_id(self, project_id:int) -> int:
        stmt = (
            delete(DataChunk)
            .where(DataChunk.chunk_project_id == project_id)
        )
        
        result = await self.db_client.execute(stmt)
        return result.rowcount or 0