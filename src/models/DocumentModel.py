from .BaseDataModel import BaseDataModel

from schemas.schemas import DocumentResponse, DocumentCreate
from models.database.document import Document
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import select,delete,update,Result, func
import math




class DocumentModel(BaseDataModel):

    def __init__(self, db_client: Session):
        super().__init__(db_client)


    async def create_document(self, document: DocumentCreate) -> DocumentResponse:

        new_document = Document(**document.model_dump())
        self.db_client.add(new_document)
        await self.db_client.flush()
        await self.db_client.refresh(new_document)
        
        return DocumentResponse.model_validate(new_document)

    async def get_document(self, document_id: int) -> DocumentResponse | None:
        stmt = select(Document).where(Document.id == document_id)
        result: Result = await self.db_client.execute(stmt)

        document = result.scalar_one_or_none()

        if document is None:
            return None

        return DocumentResponse.model_validate(document)


    async def process_document(
        self,
        document_id: int
    ) -> bool:

        stmt = (
            update(Document)
            .where(Document.id == document_id)
            .values(is_processed_to_chunks=True,updated_at= datetime.now(UTC))
        )

        result = await self.db_client.execute(stmt)

        return result.rowcount > 0

    async def delete_document(self, document_id: str) -> bool:
        stmt = delete(Document).where(Document.id == document_id)

        result = await self.db_client.execute(stmt)

        return result.rowcount > 0

    async def get_documents_by_project(self, project_id: str) -> list[DocumentResponse]:
        stmt = select(Document).where(Document.project_id == project_id)

        result: Result = await self.db_client.execute(stmt)

        documents = result.scalars().all()

        return [
            DocumentResponse.model_validate(document)
            for document in documents
        ]

    async def get_all_documents(
        self,
        page: int = 1,
        size: int = 10
    ) -> tuple[list[DocumentResponse], int]:

        if page < 1 or size < 1:
            raise ValueError("Page and size must be greater than zero")

        # 1. Get total documents count
        count_stmt = select(func.count()).select_from(Document)

        total_documents = await self.db_client.scalar(count_stmt)

        # 2. Calculate total pages
        total_pages = math.ceil(total_documents / size) if total_documents else 0

        # 3. Fetch paginated documents
        offset = (page - 1) * size

        stmt = (
             select(Document)
            .order_by(Document.updated_at.desc())
            .offset(offset)
            .limit(size)
        )

        result = await self.db_client.execute(stmt)

        documents = result.scalars().all()

        # 4. Convert ORM objects to Pydantic schemas
        response = [
            DocumentResponse.model_validate(document)
            for document in documents
        ]

        return response, total_pages

    async def delete_documents_by_project(self, project_id: int) -> int:
        stmt = delete(Document).where(Document.project_id == project_id)
        
        result = await self.db_client.execute(stmt)
        
        return result.rowcount > 0