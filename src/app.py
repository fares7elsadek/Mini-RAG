
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from routes import base, data, project, document,nlp
from helper.config import get_settings, Settings
from core.exceptions import AppException, app_exception_handler
from core.logging_config import setup_logging
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectorDbFactory import VectorDbFactory
from models.database.Base import Base


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings: Settings = get_settings()

    engine = None
    vectordb_client = None

    try:
        # Database setup
        engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_CONNECTION,
            echo=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )

        app.sessiondb_local = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # LLM setup
        llm_factory = LLMFactory()

        app.generation_model = llm_factory.create(
            provider=settings.GENERATION_BACKEND
        )
        app.generation_model.set_generation_model(
            model_id=settings.GENERATION_MODEL_ID
        )

        app.embedding_model = llm_factory.create(
            provider=settings.EMBEDDING_BACKEND
        )
        app.embedding_model.set_embedding_model(
            model_id=settings.EMBEDDING_MODEL_ID,
            embedding_size=settings.EMBEDDING_MODEL_SIZE,
        )

        # VectorDB setup
        vectordb_factory = VectorDbFactory()

        vectordb_client = vectordb_factory.create(
            provider=settings.VEC_DB_BACKEND
        )

        app.vectordb_client = vectordb_client
        vectordb_client.connect()

        logger.info("Application startup completed successfully.")

        yield

    finally:
        logger.info("Application shutdown started.")

        if vectordb_client is not None:
            try:
                vectordb_client.disconnect()
            except Exception:
                logger.exception("Failed to disconnect VectorDB.")

        if engine is not None:
            await engine.dispose()

        logger.info("Application shutdown completed.")






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
app.include_router(nlp.nlp_router)


@app.get("/health", tags=["Health"])
async def health():
    """Lightweight liveness probe (does NOT check DB)."""
    return {"status": "healthy"}
