from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME:str
    APP_VERSION:str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE_IN_MB: int
    FILE_ALLOWED_EXTENSIONS: list
    FILE_DEFAULT_CHUNK_SIZE: int
    MONGODB_URL: str
    MONGODB_DATABASE: str
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str

    class Config:
        env_file = ".env"



def get_settings():
    return Settings()