from pydantic import BaseModel, Field
from typing import Optional


class ProcessRequest(BaseModel):
    file_id: str
    chunk_size: Optional[int] = Field(default=100, gt=0, le=10000)
    overlap_size: Optional[int] = Field(default=20, ge=0)
    do_reset: bool = False