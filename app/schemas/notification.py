from uuid import UUID

from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    message: str = Field(max_length=100)


class UserPublic(BaseModel):
    first_name: str
    last_name: str


class PostPublic(BaseModel):
    title: str
    content: str
    author: UserPublic


class CommentPublic(BaseModel):
    message: str
    author: UserPublic


class NotificationResponse(NotificationBase):
    id: UUID
    message: str
    user: UserPublic
    post: PostPublic
    comment: CommentPublic
