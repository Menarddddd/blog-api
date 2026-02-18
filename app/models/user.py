import uuid
from typing import TYPE_CHECKING, List
from sqlalchemy import String, UUID, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from enum import Enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.refresh_token import RefreshToken


class Role(Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER)

    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
