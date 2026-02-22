import uuid
from typing import TYPE_CHECKING, List
from sqlalchemy import String, ForeignKey, UUID, DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone

from app.core.database import Base
from app.models.notification import Notification

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.comment import Comment


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    author: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="post", cascade="all, delete-orphan"
    )
