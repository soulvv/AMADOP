from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    post_id: int
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    username: Optional[str] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
