import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, UUID, DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("posts.id"), nullable=False)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    author: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
