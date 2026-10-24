from .BaseDataModel import BaseDataModel
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from models.enums.DataBaseEnum import DataBaseEnum
from models.database.document import Document
from bson import ObjectId




class DocumentModel(BaseDataModel):

    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.collection: AsyncIOMotorCollection  = self.db_client[DataBaseEnum.DOCUMENT_COLLECTION.value]


    async def create_document(self, document: Document) -> Document:
        result = await self.collection.insert_one(document.model_dump(by_alias=True,exclude_none=True))
        document_id = result.inserted_id
        document.id = document_id
        return document

    async def get_document(self, document_id:str) -> Document | None:
        if not ObjectId.is_valid(document_id):
            return None
        
        document = await self.collection.find_one({
            "_id":ObjectId(document_id)
        })

        if document is None:
            return None

        return Document(**document)


    async def process_document(self, document_id: str) -> bool:
        if not ObjectId.is_valid(document_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"is_processed_to_chunks": True}}
        )

        return result.matched_count > 0
       