from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    CLAUDE = "CLAUDE"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class GeminiEnums(Enum):
    USER = "user"
    MODEL = "model"