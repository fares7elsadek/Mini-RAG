from enum import Enum

class VectorDbEnums(Enum):
    QDRANT = "QDRANT"


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"