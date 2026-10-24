from pydantic import BaseModel, Field, ConfigDict
from typing import Any
from bson import ObjectId

class DataChunk(BaseModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    chunk_txt: str
    chunk_metadata: dict[str, Any]
    chunk_order: int
    chunk_project_id: ObjectId
    chunk_document_id: ObjectId

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )