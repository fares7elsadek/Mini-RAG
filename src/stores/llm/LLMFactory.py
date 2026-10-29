from llm.providers import OpenAiProvider
from helper.config import get_settings, Settings
from .LLMEnum import LLMEnums
from .LLMInterface import LLMInterface

class LLMFactory():

    def __init__(self):
        self.config: Settings = get_settings()

    def create(self, provider: str) -> LLMInterface:

        match provider:
            case LLMEnums.OPENAI.value:
                return OpenAiProvider(
                    self.config.OPENAI_KEY,
                    self.config.OPENAI_URL,
                    self.config.INPUT_DEFAULT_MAX_TOKENS,
                    self.config.GENERATE_DEFAULT_MAX_TOKENS,
                    self.config.GENERATE_DEFAULT_TEMPERATURE
                )
            case _:
                return None