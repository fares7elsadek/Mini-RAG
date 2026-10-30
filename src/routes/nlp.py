import logging
from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, Depends, Query,Request,status
from fastapi.encoders import jsonable_encoder
from core.exceptions import NotFoundException,AppException
from models import ResponseSignal
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from core.dependencies import get_project_model,get_document_model,get_vecdb,get_datachunk_model,get_embedding_llm_model
from helper.config import get_settings,Settings
from stores.vectordb.VectorDbInterface import VectorDbInterface
from stores.llm.LLMInterface import LLMInterface
from models import ProjectModel,DocumentModel,DataChunkModel
from models.database.data_chunk import DataChunk



logger = logging.getLogger(__name__)

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["NLP"],
)

vectordb_collection_name = "minirag"

def serialize(data):
    return jsonable_encoder(
        data,
        custom_encoder={ObjectId: str},
    )

@nlp_router.post("/index/{projectId}")
async def indxe_project(
    projectId:int,
    project_model: ProjectModel = Depends(get_project_model),
    document_model: DocumentModel = Depends(get_document_model),
    vector_db_client: VectorDbInterface = Depends(get_vecdb),
    data_chunk_model: DataChunkModel = Depends(get_datachunk_model),
    embedding_llm_model: LLMInterface = Depends(get_embedding_llm_model),
    settings: Settings = Depends(get_settings)
):

    # check if the project exist
    project = await project_model.get_project(project_id=projectId)
    if project is None:
        raise NotFoundException("Project", projectId)

    # get project documents 
    documents = await document_model.get_documents_by_project(project_id=project.id)

    if documents is None or len(documents) == 0:
        raise AppException(status.HTTP_400_BAD_REQUEST,f"There's no documents for project id : {projectId}")

    processed_documents = [
        doc
        for doc in documents
        if doc.is_processed_to_chunks
    ]

    if len(processed_documents) == 0:
        raise AppException(status.HTTP_400_BAD_REQUEST,f"There's no processed documents for project id : {projectId}")

    

    try:

        if not vector_db_client.is_collection_existed(vectordb_collection_name):
                vector_db_client.create_collection(collection_name=vectordb_collection_name
                                                   ,embedding_size=settings.EMBEDDING_MODEL_SIZE)

        for doc in documents:
            chunks: list[DataChunk] = await data_chunk_model.get_chunks_by_document_id(document_id=doc.id)
            if len(chunks) == 0:
                continue
    
    
            texts = [
                chunk.chunk_txt
                for chunk in chunks
            ]
    
            metadata = [
                chunk.chunk_metadata
                for chunk in chunks
            ]
    
            vectors = [
                embedding_llm_model.embed_txt(txt=txt)
                for txt in texts
            ]
    
            vector_db_client.insert_many(vectordb_collection_name,texts,vectors,metadata)

        return {
            "signal": "Project indexed",
            "indexed": True,
            "no_documents": len(documents)
         }
            

    except Exception as e:
        raise AppException(
            status_code=500,
            message="Failed to index project"
        )
    
    


    
    


