from .BaseController import BaseController
from stores.llm.LLMInterface import LLMInterface
from stores.vectordb.VectorDbInterface import VectorDbInterface
from models import DataChunkModel
from models.database.document import Document
from models.database.data_chunk import DataChunk



class NLPController(BaseController):

    def __init__(self, vector_db_client: VectorDbInterface,
                 llm_embedding_model_client: LLMInterface,
                 data_chunk_model: DataChunkModel,
                 project_id:int):

        self.vector_db_client = vector_db_client
        self.llm_embedding_model_client = llm_embedding_model_client
        self.data_chunk_model = data_chunk_model
        self.project_id = project_id


    def get_collection_name(self) -> str:
        return f"collection_{self.project_id}".strip()


    def ensure_collection_creation(self):
        collection_name = self.get_collection_name()
        if not self.vector_db_client.is_collection_existed(collection_name=collection_name):
            self.vector_db_client.create_collection(collection_name=collection_name
                                                    ,embedding_size=self.llm_embedding_model_client.embedding_size)


    async def index_project_documents(self, documents: list[Document]):
        collection_name = self.get_collection_name()

        chunks: list[DataChunk] = []
        for doc in documents:
            result = await self.data_chunk_model.get_chunks_by_document_id(document_id=doc.id)
            chunks.extend(result)

        if len(chunks) == 0:
            return False,0,0

        texts = [
            chunk.chunk_txt
            for chunk in chunks
        ]

        metadata = [
            chunk.chunk_metadata
            for chunk in chunks
        ]

        vectors = [
            self.llm_embedding_model_client.embed_txt(txt=txt)
            for txt in texts
        ]

        _ = self.vector_db_client.insert_many(collection_name,texts,vectors,metadata)
        return True, len(documents), len(chunks)

    
        