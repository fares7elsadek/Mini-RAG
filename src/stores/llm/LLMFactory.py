from llm.providers import OpenAiProvider,GeminiProvider
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
            case LLMEnums.GEMINI.value:
                return OpenAiProvider(
                    self.config.GEMINI_API_KEY,
                    default_input_max_tokens=self.config.INPUT_DEFAULT_MAX_TOKENS,
                    default_output_max_tokens=self.config.GENERATE_DEFAULT_MAX_TOKENS,
                    temperature=self.config.GENERATE_DEFAULT_TEMPERATURE
                )
            case _:
                return None