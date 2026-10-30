from ..LLMInterface import LLMInterface
from models import DocumentTypeEnum
from ..LLMEnum import GeminiEnums
from google import genai
from google.genai import types
import logging

class GeminiProvider(LLMInterface):

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

        self.client = genai.Client(
            api_key=self.api_key
        )

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str,embedding_size: int):
        self.embedding_size = embedding_size
        self.embedding_model_id = model_id

    
    def generate_txt(
        self,
        prompt: str,
        max_output_token: int = None,
        chat_history: list = None,
        temperature: float = None
    ):
        if not self.client:
            self.logger.error("Gemini client was not set.")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini was not set.")
            return None

        max_output_tokens = (
            max_output_token
            if max_output_token is not None
            else self.default_input_max_tokens
        )

        temp = (
            temperature
            if temperature is not None
            else self.default_generation_temperature
        )

        if chat_history is None:
            chat_history = []

        chat_history.append(
            self.construct_prompt(
                prompt=prompt,
                role=GeminiEnums.USER.value
            )
        )

        response = self.client.models.generate_content(
            model=self.generation_model_id,
            contents=chat_history,
            config=types.GenerateContentConfig(
                max_output_tokens=max_output_tokens,
                temperature=temp
            )
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with Gemini.")
            return None

        return response.text


    def embed_txt(self, txt:str, document_type: DocumentTypeEnum = None):

        if not self.client:
            self.logger.error("Gemini client was not set.")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for Gemini was not set.")
            return None

        response = self.client.models.embed_content(
            model=self.embedding_model_id,
            contents=txt,
            config=types.EmbedContentConfig(
                output_dimensionality=self.embedding_size
            )
        )
       
        if not response or not response.embeddings or len(response.embeddings) == 0 or not response.embeddings[0].values:
            self.logger.error("Error while embedding the txt with OpenAI")
            return None

        return response.embeddings[0].values

    def construct_prompt(self, prompt:str, role:str):
        return {
            "role": role,
            "content": self.process_txt(txt=prompt)
        }

    def process_txt(self,txt: str):
        return txt[:self.default_input_max_tokens].strip()