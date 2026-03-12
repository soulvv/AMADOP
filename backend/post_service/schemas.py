from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    author_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
