from fastapi import Depends, Request
from stores.vectordb.VectorDbInterface import VectorDbInterface
from controllers import ProcessController, ProjectController, NLPController
from models import DocumentModel, DataChunkModel, ProjectModel
from stores.llm.LLMInterface import LLMInterface
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request):
    """Return the DB database instance attached during lifespan."""
    async with request.app.sessiondb_local() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


def get_vecdb(request: Request) -> VectorDbInterface:
    """Return the VectorDb database instance attached during lifespan."""
    return request.app.vectordb_client

def get_embedding_llm_model(request: Request) -> LLMInterface:
    """Return the Embedding LLM Model instance attached during lifespan."""
    return request.app.embedding_model

def get_generation_llm_model(request: Request) -> LLMInterface:
    """Return the Generation LLM Model instance attached during lifespan."""
    return request.app.generation_model

def get_project_controller(db: AsyncSession = Depends(get_db)) -> ProjectController:
    return ProjectController(db_client=db)

def get_nlp_controller(request: Request, project_id: int, db: AsyncSession = Depends(get_db)) -> NLPController:
    return NLPController(vector_db_client=get_vecdb(request),
                         llm_embedding_model_client=get_embedding_llm_model(request),
                         llm_generation_model_client=get_generation_llm_model(request),
                         data_chunk_model=DataChunkModel(db_client=db), project_id=project_id)


def get_document_model(db: AsyncSession = Depends(get_db)) -> DocumentModel:
    return DocumentModel(db_client=db)

def get_project_model(db: AsyncSession = Depends(get_db)) -> ProjectModel:
    return ProjectModel(db_client=db)

def get_datachunk_model(db: AsyncSession = Depends(get_db)) -> DataChunkModel:
    return DataChunkModel(db_client=db)

def get_process_controller(request: Request, project_id: str) -> ProcessController:
    return ProcessController(project_id=project_id)