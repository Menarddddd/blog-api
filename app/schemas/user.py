import uuid
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.models.user import Role


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    username: str = Field(min_length=7, max_length=200)
    role: Role


class UserCreate(UserBase):
    password: str = Field(min_length=5, max_length=200)


class UserPublic(BaseModel):
    first_name: str
    last_name: str


class CommentPublicPost(BaseModel):
    message: str
    author: UserPublic
    date_created: datetime


class PostPublic(BaseModel):
    title: str
    content: str
    date_created: datetime
    comments: List[CommentPublicPost]


class CommentPublic(BaseModel):
    message: str
    author: UserPublic
    post: PostPublic


class TokenPublic(BaseModel):
    hashed_token: str


class UserResponse(UserBase):
    id: uuid.UUID
    posts: List[PostPublic] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserResponseWithActivity(UserBase):
    id: uuid.UUID
    posts: List[PostPublic] = Field(default_factory=list)
    comments: List[CommentPublic] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=5, max_length=200)
    confirm_password: str = Field(min_length=5, max_length=200)
