from .BaseController import BaseController
from stores.llm.LLMInterface import LLMInterface
from stores.vectordb.VectorDbInterface import VectorDbInterface
from models import DataChunkModel
from models.database.document import Document
from models.database.data_chunk import DataChunk



class NLPController(BaseController):

    def __init__(self, vector_db_client: VectorDbInterface,
                 llm_embedding_model_client: LLMInterface,
                 llm_generation_model_client: LLMInterface,
                 data_chunk_model: DataChunkModel,
                 project_id:int):

        self.vector_db_client = vector_db_client
        self.llm_embedding_model_client = llm_embedding_model_client
        self.data_chunk_model = data_chunk_model
        self.project_id = project_id
        self.llm_generation_model_client = llm_generation_model_client
        self.RAG_PROMPT = """
            You are an AI assistant that answers questions based on the provided context.

            Your task is to answer the user's question using ONLY the information
            available in the provided context.

            ### Instructions:
            1. Carefully read all provided context chunks.
            2. Answer the question using relevant information from the context.
            3. Do not use external knowledge or make assumptions.
            4. If the context does not contain enough information to answer,
            explicitly say that you don't have enough information.
            5. If multiple context chunks contain relevant information, combine
            them into a clear and coherent answer.
            6. Do not invent facts, numbers, names, or details.
            7. Keep your answer clear, accurate, and concise.

            ### Context:
            {context}

            ### User Question:
            {question}

            ### Answer:
        """


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

    
    def search_in_vectordb(self, txt: str, limit: int):

        # get collection name
        self.ensure_collection_creation()
        collection_name = self.get_collection_name()

        # get embedding
        vector = self.llm_embedding_model_client.embed_txt(
            txt=txt
        )

        if len(vector) == 0:
            return False

        # search
        result = self.vector_db_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        return result

    def build_rag_prompt(
        self,
        chunks: list[str],
        question: str
    ) -> str:

        if not chunks:
            return None

        context = "\n\n".join(
            f"[Chunk {index + 1}]\n{chunk}"
            for index, chunk in enumerate(chunks)
        )

        prompt = self.RAG_PROMPT.format(
            context=context,
            question=question
        )

        return prompt

    def get_llm_answer(self, user_prompt: str) -> str:

        retrieved_documents = self.search_in_vectordb(
            txt= user_prompt,
            limit=5
        )

        chunks = [
            doc.text
            for doc in retrieved_documents
        ]

        final_prompt = self.build_rag_prompt(
            chunks=chunks,
            question=user_prompt
        )

        llm_answer = self.llm_generation_model_client.generate_txt(
            prompt=final_prompt
        )

        return llm_answer