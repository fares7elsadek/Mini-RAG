from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.database import Document
from fastapi import HTTPException

class ProcessController(BaseController):


    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController.get_project_path(project_id=project_id)
        


    def get_file_extension(self, file_id:str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file: Document):

        document: Document = file

        if document is None:
            raise HTTPException(401, f"Document with id {file_id} not found.")

        ext = self.get_file_extension(file_id=document.document_name)
        file_path = document.document_path

        match ext:
            case ProcessingEnum.PDF.value:
                return PyMuPDFLoader(file_path=file_path)
            case ProcessingEnum.TXT.value:
                return TextLoader(file_path=file_path,encoding="utf-8")
            case _ :
                return None


    def get_file_content(self, file: Document):
        loader = self.get_file_loader(file=file)
        return loader.load()


    def process_file_content(self, file_content: list, file_id: str, 
                             chunk_size: int = 100, overlap: int = 20):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len
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
            metadatas=file_content_metadata
        )

        return chunks

