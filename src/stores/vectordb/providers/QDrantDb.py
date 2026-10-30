from ..VectorDbInterface import VectorDbInterface
from typing import List
import logging
from ..VectorDBEnum import DistanceMethodEnums
from qdrant_client import QdrantClient, models
from uuid import uuid4

class QDrantDbProvider(VectorDbInterface):

    def __init__(self, db_path: str, distance_method: DistanceMethodEnums = DistanceMethodEnums.COSINE):
        self.client: QdrantClient = None
        self.db_path = db_path
        self.distance_method = None

        match distance_method:
            case DistanceMethodEnums.COSINE:
                self.distance_method = models.Distance.COSINE
            case DistanceMethodEnums.DOT:
                self.distance_method = models.Distance.DOT
            case _:
                pass

        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self)-> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False) -> bool:
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method,
                )
            )

            return True

        return False


    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list[float],
        metadata: dict = None,
        record_id: str = None
    ) -> bool:

        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error("Collection does not exist.")
            return False

        point = models.PointStruct(
            id= record_id or str(uuid4()),
            vector=vector,
            payload={
                "text": text,
                "metadata": metadata or {}
            }
        )

        self.client.upsert(
            collection_name=collection_name,
            points=[point]
        )

        return True


    def insert_many(
        self,
        collection_name: str,
        texts: list[str],
        vectors: list[list[float]],
        metadata: list[dict] = None,
        record_ids: list[str] = None,
        batch_size: int = 50
    ) -> bool:

        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error("Collection does not exist.")
            return False

        # Validate inputs
        if len(texts) != len(vectors):
            self.logger.error("Texts and vectors must have the same length.")
            return False

        if metadata is not None and len(metadata) != len(texts):
            self.logger.error("Metadata and texts must have the same length.")
            return False

        if record_ids is not None and len(record_ids) != len(texts):
            self.logger.error("Record IDs and texts must have the same length.")
            return False

        if batch_size <= 0:
            self.logger.error("Batch size must be greater than zero.")
            return False

        for i in range(0, len(texts), batch_size):

            end = i + batch_size

            points = [
                models.PointStruct(
                    id=(
                        record_ids[j]
                        if record_ids is not None and record_ids[j]
                        else str(uuid4())
                    ),
                    vector=vectors[j],
                    payload={
                        "text": texts[j],
                        "metadata": (
                            metadata[j] if metadata is not None and metadata[j] is not None
                            else {}
                        )
                    }
                )
                for j in range(i, min(end, len(texts)))
            ]

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )

        return True


    def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 5
    ):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error("Collection does not exist.")
            return False

        results = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "text": point.payload.get("text"),
                "metadata": point.payload.get("metadata", {})
            }
            for point in results.points
        ]

        