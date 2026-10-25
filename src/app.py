import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from routes import base, data, project, document
from helper.config import get_settings, Settings
from core.exceptions import AppException, app_exception_handler
from core.logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    settings: Settings = get_settings()

    client = AsyncIOMotorClient(settings.MONGODB_CONNECTION_STRING)

    try:
        # Verify MongoDB is reachable
        await client.admin.command("ping")
        logger.info("Connected to MongoDB successfully.")

        app.state.mongo_client = client
        app.state.mongodb = client.get_database(settings.MONGODB_DATABASE_NAME)
        

        # Ensure indexes exist (idempotent — safe to call on every startup)
        await _ensure_indexes(app.state.mongodb)

        yield

    finally:
        logger.info("Shutting down — closing MongoDB connection.")
        client.close()


async def _ensure_indexes(db) -> None:
    await db["projects"].create_index("project_id", unique=True)
    await db["documents"].create_index("project_id")
    await db["chunks"].create_index("chunk_document_id")
    logger.info("MongoDB indexes ensured.")


app = FastAPI(
    title="Mini-RAG",
    version="1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)



app.add_exception_handler(AppException, app_exception_handler)



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(project.project_router)
app.include_router(document.document_router)


@app.get("/health", tags=["Health"])
async def health():
    """Lightweight liveness probe (does NOT check DB)."""
    return {"status": "healthy"}
