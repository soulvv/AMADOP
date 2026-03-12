from pydantic import BaseModel, Field
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: int
    message: str = Field(..., min_length=1, max_length=500)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
