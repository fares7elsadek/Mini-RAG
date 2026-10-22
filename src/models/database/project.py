from pydantic import BaseModel,field_validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):

    _id: Optional[ObjectId]
    project_id: str

    @field_validator("project_id")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("'project_id' must be alphanumric.")
        return value

    class Config:
        arbitrary_types_allowed = True