import logging
import os

from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.enums.DataBaseEnum import DocumentTypeEnum
from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProcessingEnum
from models.database import Document
from core.exceptions import FileProcessingException, NotFoundException

logger = logging.getLogger(__name__)


class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController.get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str) -> str:
        return os.path.splitext(file_id)[-1]

    def get_file_type(self, file_id: str) -> DocumentTypeEnum:
        """Return the file type based on the file extension."""
        ext = self.get_file_extension(file_id=file_id).lower()

        match ext:
            case ".pdf":
                return DocumentTypeEnum.PDF
            case ".txt":
                return DocumentTypeEnum.TXT
            case _:
                raise FileProcessingException(
                    f"Unsupported file type: '{ext}'. "
                    f"Supported types: {[e.value for e in DocumentTypeEnum]}"
                )

    def get_file_size(self, file_path: str) -> int:
        """Return the size of the file in bytes."""
        if not os.path.exists(file_path):
            raise NotFoundException("File", file_path)
        return os.path.getsize(file_path)

    def get_file_loader(self, file: Document):
        """Return the appropriate LangChain document loader for the file type.

        Raises FileProcessingException if the file type is not supported.
        """
        ext = self.get_file_extension(file_id=file.document_name)
        file_path = file.document_path

        match ext:
            case ProcessingEnum.PDF.value:
                return PyMuPDFLoader(file_path=file_path)
            case ProcessingEnum.TXT.value:
                return TextLoader(file_path=file_path, encoding="utf-8")
            case _:
                raise FileProcessingException(
                    f"Unsupported file type: '{ext}'. "
                    f"Supported types: {[e.value for e in ProcessingEnum]}"
                )

    def get_file_content(self, file: Document):
        """Load and return the document content using the appropriate loader."""
        loader = self.get_file_loader(file=file)
        return loader.load()

    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        overlap: int = 20,
    ):
        """Split document content into chunks for embedding."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
        )

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(
            texts=file_content_texts,
            metadatas=file_content_metadata,
        )

        return chunks
