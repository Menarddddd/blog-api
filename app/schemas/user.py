import uuid
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class UserBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    username: str = Field(min_length=7, max_length=200)


class UserCreate(UserBase):
    password: str = Field(min_length=5, max_length=200)


class PostPublic(BaseModel):
    title: str
    content: str
    date_created: datetime


class TokenPublic(BaseModel):
    hashed_token: str


class UserResponse(UserBase):
    posts: List[PostPublic] = Field(default_factory=list)
    refresh_tokens: List[TokenPublic] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
