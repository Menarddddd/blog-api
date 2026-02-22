from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.user import User
from app.repositories.comment import (
    create_comment_db,
    delete_comment_by_id_db,
    get_all_comments_db,
    get_comment_by_id_db,
    get_my_comments_db,
    update_comment_db,
)
from app.repositories.notification import create_notification_db
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.notification import create_notification_service
from app.services.post import get_post_service


# ADMIN
async def get_comments_admin_service(db: AsyncSession):
    comments = await get_all_comments_db(db)
    return comments


async def delete_comment_admin_service(comment_id: UUID, db: AsyncSession):
    await delete_comment_by_id_db(comment_id, db)


async def create_comment_service(
    post_id: UUID,
    form_data: CommentCreate,
    db: AsyncSession,
    current_user: User,
):
    post = await get_post_service(post_id, db, current_user)
    comment = Comment(message=form_data.message, author=current_user, post=post)
    new_comment = await create_comment_db(comment, db)
    loaded_comment = await get_comment_by_id_db(new_comment.id, db)

    if current_user.id != post.author.id:
        notification = create_notification_service(current_user, post, loaded_comment)
        await create_notification_db(notification, db)

    return loaded_comment


async def my_comments_service(db: AsyncSession, current_user: User):
    comments = await get_my_comments_db(current_user, db)

    return comments


async def get_comment_service(comment_id: UUID, db: AsyncSession):
    comment = await get_comment_by_id_db(comment_id, db)

    return comment


async def update_comment_service(
    form_data: CommentUpdate, comment_id: UUID, db: AsyncSession, current_user: User
):
    comment = await get_comment_by_id_db(comment_id, db)

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot update this comment",
        )

    data = form_data.model_dump(exclude_unset=True)
    updated_comment = await update_comment_db(data, comment, db)

    return updated_comment


async def delete_comment_service(
    current_user: User, comment_id: UUID, db: AsyncSession
):
    comment = await get_comment_by_id_db(comment_id, db)
    if current_user.id != comment.user_id and current_user.id != comment.post.author.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this comment.",
        )

    await db.delete(comment)
    await db.commit()
