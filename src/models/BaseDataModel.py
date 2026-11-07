from helper.config import get_settings,Settings
from sqlalchemy.ext.asyncio import AsyncSession

class BaseDataModel:

    def __init__(self, db_client: AsyncSession):
        self.db_client = db_client
        self.app_settings: Settings = get_settings()