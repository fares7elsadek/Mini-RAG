from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE_IN_MB: int
    FILE_ALLOWED_EXTENSIONS: list
    FILE_DEFAULT_CHUNK_SIZE: int
    MONGODB_CONNECTION_STRING: str
    MONGODB_DATABASE_NAME: str
    GENERATION_BACKEND:str
    EMBEDDING_BACKEND:str
    OPENAI_KEY:str = None
    OPENAI_URL:str = None
    GENERATION_MODEL_ID:str = None
    EMBEDDING_MODEL_ID:str = None
    EMBEDDING_MODEL_SIZE:str = None
    INPUT_DEFAULT_MAX_TOKENS:int = None
    GENERATE_DEFAULT_MAX_TOKENS:int = None
    GENERATE_DEFAULT_TEMPERATURE:int = None
    VEC_DB_PATH:str
    VEC_DB_DISTANCE_METHOD:str
    VEC_DB_BACKEND:str
    
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()