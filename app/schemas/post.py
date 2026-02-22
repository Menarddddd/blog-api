from datetime import datetime
from typing import List
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


class CommentPublic(BaseModel):
    id: UUID
    message: str
    author: UserPublic


class PostResponse(PostBase):
    id: UUID
    date_created: datetime
    author: UserPublic
    comments: List[CommentPublic]


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
