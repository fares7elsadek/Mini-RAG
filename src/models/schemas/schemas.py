
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from models.enums.DataBaseEnum import DocumentTypeEnum



class ORMBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)



class ProjectBase(BaseModel):
    project_name: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the project",
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class ProjectResponse(ORMBaseSchema, ProjectBase):
    id: int
    is_indexed: bool
    created_at: datetime
    updated_at: datetime



class DocumentBase(BaseModel):
    document_name: str = Field(min_length=1, max_length=255)
    document_path: str = Field(min_length=1)
    document_type: DocumentTypeEnum
    document_size: int = Field(ge=0)


class DocumentCreate(DocumentBase):
    project_id: int = Field(gt=0)


class DocumentUpdate(BaseModel):
    document_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class DocumentResponse(ORMBaseSchema, DocumentBase):
    id: int
    project_id: int
    uploaded_at: datetime
    updated_at: datetime
    is_processed_to_chunks: bool



class DataChunkBase(BaseModel):
    chunk_txt: str = Field(min_length=1)
    chunk_metadata: dict[str, Any] = Field(default_factory=dict)
    chunk_order: int = Field(ge=0)


class DataChunkCreate(DataChunkBase):
    chunk_project_id: int = Field(gt=0)
    chunk_document_id: int = Field(gt=0)


class DataChunkResponse(ORMBaseSchema, DataChunkBase):
    id: int
    chunk_project_id: int
    chunk_document_id: int


class DocumentDetailResponse(DocumentResponse):
    project: ProjectResponse


class DataChunkDetailResponse(DataChunkResponse):
    document: DocumentDetailResponse
    project: ProjectResponse
