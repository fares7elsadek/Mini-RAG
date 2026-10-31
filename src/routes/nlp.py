import logging
from fastapi import APIRouter, Depends,status
from core.exceptions import NotFoundException,AppException
from models import ResponseSignal
from core.dependencies import get_project_model,get_document_model,get_nlp_controller
from models import ProjectModel,DocumentModel
from .schemas.nlp import SearchRequest
from controllers import NLPController



logger = logging.getLogger(__name__)

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["NLP"],
)

@nlp_router.post("/index/{project_Id}")
async def indxe_project(
    project_id: int,
    project_model: ProjectModel = Depends(get_project_model),
    document_model: DocumentModel = Depends(get_document_model),
    nlp_controller: NLPController = Depends(get_nlp_controller),
):

    # check if the project exist
    project = await project_model.get_project(project_id=project_id)
    if project is None:
        raise NotFoundException("Project", project_id)

    # check if the project indexed before
    if project.is_indexed:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message= ResponseSignal.PROJECT_INDEXED_BEFORE.value
        )

    # get project documents 
    documents = await document_model.get_documents_by_project(project_id=project.id)

    if documents is None or len(documents) == 0:
        raise AppException(status.HTTP_400_BAD_REQUEST,f"There's no documents for project id : {project_id}")

    processed_documents = [
        doc
        for doc in documents
        if doc.is_processed_to_chunks
    ]

    if len(processed_documents) == 0:
        raise AppException(status.HTTP_400_BAD_REQUEST,f"There's no processed documents for project id : {project_id}")

    try:

        _ = nlp_controller.ensure_collection_creation()

        success, no_documents , no_chunks = await nlp_controller.index_project_documents(
            documents=documents
        )

        if success:
           matched = await project_model.index_project(project_id=project.id)
           if not matched:
               raise AppException(
                   status.HTTP_400_BAD_REQUEST,
                   ResponseSignal.PROJECT_INDEX_FAILED.value
               )

        return {
            "signal": ResponseSignal.PROJECT_CREATION_SUCCESS.value,
            "indexed": success,
            "no_documents": no_documents,
            "no_chunks": no_chunks
        }
            

    except Exception as e:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=ResponseSignal.PROJECT_INDEX_FAILED.value
        )
    
    

@nlp_router.post("/search/{project_id}")
async def search_in_vectordb(
    project_id: int,
    search_request: SearchRequest,
    project_model: ProjectModel = Depends(get_project_model),
    nlp_controller: NLPController = Depends(get_nlp_controller)
):

    # check if the project exist
    project = await project_model.get_project(project_id=project_id)
    if project is None:
        raise NotFoundException("Project", project_id)

    if not project.is_indexed:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message= ResponseSignal.PROJECT_IS_NOT_INDEXED.value
        )
    
    try:
    
        result = nlp_controller.search_in_vectordb(
            txt=search_request.text,
            limit=search_request.limit
        )

        if not result:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=ResponseSignal.PROJECT_SEARCH_FAILED.value
            )

        return {
            "signal": ResponseSignal.PROJECT_SEARCH_SUCCESS.value,
            "content": result,
        }
            

    except Exception as e:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=ResponseSignal.PROJECT_SEARCH_FAILED.value
        )
    


