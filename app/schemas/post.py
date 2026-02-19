from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str = Field(max_length=200)
    content: str


class PostCreate(PostBase):
    pass


class UserPublic(BaseModel):
    first_name: str
    last_name: str


class PostResponse(PostBase):
    id: UUID
    date_created: datetime
    author: UserPublic


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
