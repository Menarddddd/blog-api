from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post


async def create_post_db(post: Post, db: AsyncSession):
    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post


async def get_all_post_db(db: AsyncSession):
    result = await db.execute(select(Post).options(selectinload(Post.author)))
    posts = result.scalars().all()

    return posts


async def get_post_by_id_db(post_id: UUID, db: AsyncSession):
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return post


async def update_post_db(to_update: dict, post: Post, db: AsyncSession):
    for key, value in to_update.items():
        setattr(post, key, value)

    await db.commit()
    await db.refresh(post)

    return post


async def delete_post_db(post_id: UUID, db: AsyncSession):
    post = await get_post_by_id_db(post_id, db)

    await db.delete(post)
    await db.commit()
