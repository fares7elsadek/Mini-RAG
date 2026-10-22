from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

class DataChunk(BaseModel):

    _id: Optional[ObjectId]
    chunk_txt: str
    chunk_metadata: str
    chunk_order: int
    chunk_project_id: ObjectId

    class Config:
        arbitrary_types_allowed = True