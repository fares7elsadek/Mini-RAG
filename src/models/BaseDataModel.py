from helper.config import get_settings,Settings
from sqlalchemy.orm import Session

class BaseDataModel:

    def __init__(self, db_client: Session):
        self.db_client = db_client
        self.app_settings: Settings = get_settings()