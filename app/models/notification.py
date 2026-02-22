import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, UUID, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post
    from app.models.comment import Comment


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("posts.id"), nullable=False)
    comment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("comments.id"), nullable=False
    )
    message: Mapped[str] = mapped_column(String(100), nullable=False)
    notification_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="notifications")
    post: Mapped["Post"] = relationship("Post", back_populates="notifications")
    comment: Mapped["Comment"] = relationship("Comment", back_populates="notifications")
