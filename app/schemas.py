import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from fastapi_users import schemas


class PostResponse(BaseModel):
    id: uuid.UUID
    caption: Optional[str] = None
    url: str
    file_type: str
    file_name: str
    created_at: datetime
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass