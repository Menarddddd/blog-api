from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.notification import Notification
from app.models.post import Post
from app.models.user import User


async def create_notification_db(notification: Notification, db: AsyncSession):
    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    return notification


async def get_all_notification_db(current_user: User, db: AsyncSession):
    stmt = (
        select(Notification)
        .options(
            selectinload(Notification.user),
            selectinload(Notification.post).selectinload(Post.author),
            selectinload(Notification.comment).options(selectinload(Comment.author)),
        )
        .where(Notification.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    return notifications


async def get_notification_by_id_db(
    notification_id: UUID, db: AsyncSession
) -> Notification:
    stmt = (
        select(Notification)
        .options(
            selectinload(Notification.user),
            selectinload(Notification.post).selectinload(Post.author),
            selectinload(Notification.comment).options(selectinload(Comment.author)),
        )
        .where(Notification.id == notification_id)
    )
    result = await db.execute(stmt)
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    return notification


async def clear_all_notification_db(current_user: User, db: AsyncSession):
    await db.execute(
        delete(Notification).where(Notification.user_id == current_user.id)
    )
    await db.commit()


async def delete_notification_by_id_db(notification_id: UUID, db: AsyncSession):
    notification = await get_notification_by_id_db(notification_id, db)
    await db.delete(notification)
    await db.commit()
