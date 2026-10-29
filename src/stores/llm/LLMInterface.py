from abc import ABC, abstractmethod
from models import DocumentTypeEnum

class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        pass

    @abstractmethod
    def generate_txt(self, prompt: str, max_output_token: int = None, chat_history: list[str] = [], temperature: float = None):
        pass

    @abstractmethod
    def embed_txt(self, txt:str, document_type: DocumentTypeEnum = None):
        pass

    @abstractmethod
    def construct_prompt(self, prompt:str, role:str):
        pass