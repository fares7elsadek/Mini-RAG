from .Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer,String,DateTime,Boolean
from datetime import UTC, datetime
from .document import Document
from .data_chunk import DataChunk


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_name: Mapped[str] = mapped_column(String(100), nullable=False)
    project_id:  Mapped[int] = mapped_column(Integer,nullable=False)
    is_indexed: Mapped[bool] = mapped_column(Boolean,nullable=False,default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default= lambda: datetime.now(UTC)
    )

    documents: Mapped[Document] = relationship(back_populates="project")
    chunks: Mapped[DataChunk] = relationship(back_populates="project")

   