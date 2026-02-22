from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    message: str


class CommentCreate(CommentBase):
    pass


class UserPublic(BaseModel):
    first_name: str
    last_name: str


class PostPublic(BaseModel):
    title: str
    content: str
    author: UserPublic


class CommentResponse(CommentBase):
    id: UUID
    author: UserPublic
    post: PostPublic

    model_config = ConfigDict(from_attributes=True)


class CommentUpdate(BaseModel):
    message: str
