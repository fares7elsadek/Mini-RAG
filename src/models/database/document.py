
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from models.enums.DataBaseEnum import DocumentTypeEnum


class Document(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )

    id: ObjectId | None = Field(default=None, alias="_id")
    project_id: ObjectId
    document_name: str
    document_path: str
    document_type: DocumentTypeEnum 
    document_size: int
    uploaded_at: datetime
    updated_at: datetime
    is_processed_to_chunks: bool = False
