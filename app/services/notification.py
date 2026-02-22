from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.notification import Notification
from app.models.post import Post
from app.models.user import User
from app.repositories.notification import (
    clear_all_notification_db,
    delete_notification_by_id_db,
    get_all_notification_db,
    get_notification_by_id_db,
)


def create_notification_service(current_user: User, post: Post, comment: Comment):
    message = (
        f"{current_user.first_name} { current_user.last_name } commented on your post"
    )

    notification = Notification(
        message=message,
        user_id=post.author.id,
        post_id=post.id,
        comment_id=comment.id,
    )

    return notification


async def my_notifications_service(db: AsyncSession, current_user: User):
    notifications = await get_all_notification_db(current_user, db)

    return notifications


async def clear_notifications_service(db: AsyncSession, current_user: User):
    await clear_all_notification_db(current_user, db)


async def get_notification_service(
    notification_id: UUID, db: AsyncSession, current_user: User
):
    notification = await get_notification_by_id_db(notification_id, db)

    return notification


async def delete_notification_service(notification_id: UUID, db: AsyncSession):
    await delete_notification_by_id_db(notification_id, db)
