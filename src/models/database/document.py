
from .Base import Base
from models.enums.DataBaseEnum import DocumentTypeEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer,String,Enum,DateTime,Boolean
from .project import Project
from datetime import UTC, datetime


class Document(Base):

    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id")
    )

    document_name: Mapped[str] = mapped_column(String(100), nullable=False)
    document_path: Mapped[str] = mapped_column(String(200), nullable=False)
    document_type: Mapped[DocumentTypeEnum] = mapped_column(Enum(DocumentTypeEnum),nullable=False)
    document_size: Mapped[int] = mapped_column(Integer,nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default= lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default= lambda: datetime.now(UTC)
    )
    is_processed_to_chunks: Mapped[bool] = mapped_column(Boolean,nullable=False,default=False)

    project: Mapped[Project] = relationship(back_populates="documents")
