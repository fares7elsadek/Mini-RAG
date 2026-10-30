from .providers import QDrantDbProvider
from helper.config import get_settings, Settings
from .VectorDBEnum import VectorDbEnums, DistanceMethodEnums
from .VectorDbInterface import VectorDbInterface
from controllers.BaseController import BaseController

class VectorDbFactory():

    def __init__(self):
        self.config: Settings = get_settings()

        self.distance_method: DistanceMethodEnums = None

        match self.config.VEC_DB_DISTANCE_METHOD:
            case "COSINE":
                self.distance_method = DistanceMethodEnums.COSINE
            case "DOT":
                self.distance_method = DistanceMethodEnums.DOT
            case _:
                pass

        self.base_controller = BaseController()

    def create(self, provider: str) -> VectorDbInterface:
        match provider:
            case VectorDbEnums.QDRANT.value:
                db_path = self.base_controller.get_database_path(self.config.VEC_DB_PATH)
                return QDrantDbProvider(
                    db_path=db_path,
                    distance_method=self.distance_method
                )
            case _:
                return None