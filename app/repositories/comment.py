from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate

# Continue this later, we are seperating the concern of db transactions


async def create_comment_db(comment: Comment, db: AsyncSession):
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment


async def get_comment_by_id_db(comment_id: UUID, db: AsyncSession) -> Comment:
    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.post).options(selectinload(Post.author)),
        )
        .where(Comment.id == comment_id)
    )
    result = await db.execute(stmt)
    comment = result.scalars().first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    return comment


async def get_my_comments_db(current_user: User, db: AsyncSession):
    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.post).options(selectinload(Post.author)),
        )
        .where(Comment.user_id == current_user.id)
    )

    result = await db.execute(stmt)
    comments = result.scalars().all()

    return comments


async def get_all_comments_db(db: AsyncSession):
    stmt = select(Comment).options(
        selectinload(Comment.author),
        selectinload(Comment.post).options(selectinload(Post.author)),
    )

    result = await db.execute(stmt)
    comments = result.scalars().all()

    return comments


async def delete_comment_by_id_db(id: UUID, db: AsyncSession):
    comment = await get_comment_by_id_db(id, db)

    await db.delete(comment)
    await db.commit()


async def update_comment_db(
    form_data: dict, comment: Comment, db: AsyncSession
) -> Comment:
    for key, value in form_data.items():
        setattr(comment, key, value)

    await db.commit()
    await db.refresh(comment)

    return comment
