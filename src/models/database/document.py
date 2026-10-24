
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


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
    is_processed_to_chunks: bool = False
