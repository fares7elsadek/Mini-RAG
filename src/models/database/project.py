from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
from datetime import datetime


class Project(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )

    id: ObjectId | None = Field(default=None, alias="_id")

    project_name: str = Field(
        min_length=3,
        max_length=100,
    )
    project_id: int
    is_indexed: bool = Field(default=False)
    updated_at: datetime | None = None

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Project name cannot be empty or whitespace.")

        return value.strip()

   