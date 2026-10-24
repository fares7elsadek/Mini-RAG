from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from controllers import ProjectController
from models import DocumentModel, DataChunkModel


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Return the MongoDB database instance attached during lifespan."""
    return request.app.state.mongodb


def get_project_controller(request: Request) -> ProjectController:
    return ProjectController(db_client=get_db(request))


def get_document_model(request: Request) -> DocumentModel:
    return DocumentModel(db_client=get_db(request))


def get_datachunk_model(request: Request) -> DataChunkModel:
    return DataChunkModel(db_client=get_db(request))
