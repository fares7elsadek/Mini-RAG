
from typing import Any, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base

if TYPE_CHECKING:
    from .project import Project
    from .document import Document


class DataChunk(Base):
    __tablename__ = "data_chunks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    chunk_txt: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict
    )

    chunk_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    chunk_project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    project: Mapped["Project"] = relationship(
        back_populates="chunks"
    )

    document: Mapped["Document"] = relationship(
        back_populates="chunks"
    )
