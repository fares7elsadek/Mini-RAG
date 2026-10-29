from ..LLMInterface import LLMInterface
from openai import OpenAI
from models import DocumentTypeEnum
from ..LLMEnum import OpenAIEnums
import logging

class OpenAiProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: str=None,
                 default_input_max_tokens: int = 1000,
                 default_output_max_tokens: int = 1000,
                 temperature: float = 0.1):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_tokens = default_input_max_tokens
        self.default_output_max_tokens = default_output_max_tokens
        self.default_generation_temperature = temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            api_url=self.api_url
        )

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str,embedding_size: int):
        self.embedding_size = embedding_size
        self.embedding_model_id = model_id

    def generate_txt(self, prompt: str, max_output_token: int = None, chat_history: list[str] = [], temperature: float = None):
        if not self.client:
            self.logger.error("OpenAI client was not set.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set.")
            return None

        max_output_tokens = max_output_token if max_output_token else self.default_input_max_tokens
        temp = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt,role=OpenAIEnums.USER.value)
        )

        response = self.client.completions.create(
            model=  self.generation_model_id,
            messages = chat_history,
            max_tokens= max_output_tokens,
            temperature= temp
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generate the txt with OpenAI")
            return None

        return response.choices[0].message["content"]

    def embed_txt(self, txt:str, document_type: DocumentTypeEnum = None):

        if not self.client:
            self.logger.error("OpenAI client was not set.")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set.")
            return None

        response = self.client.embeddings.create(
            model= self.embedding_model_id,
            input=txt
        )

        if not response or not response.data or len(response.data) == 0 or not response[0].embedding:
            self.logger.error("Error while embedding the txt with OpenAI")
            return None

        return response[0].embedding

    def construct_prompt(self, prompt:str, role:str):
        return {
            "role": role,
            "content": self.process_txt(txt=prompt)
        }

    def process_txt(self,txt: str):
        return txt[:self.default_input_max_tokens].strip()