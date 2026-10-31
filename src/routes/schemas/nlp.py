from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = Field(default=5,gt=0,le=10)

class QuestionRequest(BaseModel):
    prompt: str