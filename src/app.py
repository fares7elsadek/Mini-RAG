
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from routes import base, data
from helper.config import get_settings, Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = get_settings()

    client = AsyncMongoClient(settings.MONGODB_URL)

    try:
        # Verify MongoDB is reachable
        await client.admin.command("ping")

        app.state.mongo_client = client
        app.state.mongodb = client.get_default_database()

        yield

    finally:
        await client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
