from typing import Literal
from pydantic import BaseModel, Field


class Correction(BaseModel):
    status: Literal['suggestions', 'no_suggestion', 'partial', 'unavailable']
    original: str = Field(max_length=2000)
    suggested: str | None = Field(default=None, max_length=4000)
    processed: int = Field(default=0, ge=0, le=12)
    skipped: int = Field(default=0, ge=0)
