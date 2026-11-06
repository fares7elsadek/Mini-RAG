from .Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Any
from sqlalchemy import ForeignKey, Integer, Text, JSON
from .project import Project
from .document import Document

class DataChunk(Base):
    __tablename__ = "data_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chunk_txt: Mapped[str] = mapped_column(Text,nullable=False)
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable= True)
    chunk_order: Mapped[int] = mapped_column(Integer)


    chunk_project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )
    chunk_document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True
    )

    project: Mapped[Project] = relationship(back_populates="chunks")
    document: Mapped[Document] = relationship(back_populates="chunks")