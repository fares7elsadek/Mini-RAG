from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.enums.DataBaseEnum import DocumentTypeEnum
from .Base import Base

if TYPE_CHECKING:
    from .data_chunk import DataChunk
    from .project import Project


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    document_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    document_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    document_type: Mapped[DocumentTypeEnum] = mapped_column(
        Enum(DocumentTypeEnum, name="document_type_enum"),
        nullable=False
    )

    document_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    is_processed_to_chunks: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    project: Mapped["Project"] = relationship(
        back_populates="documents"
    )

    chunks: Mapped[list["DataChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )