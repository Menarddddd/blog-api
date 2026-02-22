from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.models.user import User
from app.repositories.post import (
    create_post_db,
    delete_post_admin_db,
    delete_post_db,
    feed_post_db,
    get_all_post_db,
    get_post_by_id_db,
    update_post_db,
)
from app.schemas.post import PostCreate, PostUpdate


async def create_post_service(
    form_data: PostCreate, db: AsyncSession, current_user: User
):
    data = form_data.model_dump()
    new_post = Post(**data)
    new_post.user_id = current_user.id

    post = await create_post_db(new_post, db)

    return post


async def my_posts_service(db: AsyncSession, current_user: User):
    posts = await get_all_post_db(current_user.id, db)

    return posts


async def get_post_service(post_id: UUID, db: AsyncSession, current_user: User):
    post = await get_post_by_id_db(post_id, db)

    return post


async def update_post_service(
    form_data: PostUpdate, post_id: UUID, db: AsyncSession, current_user: User
):
    post = await get_post_by_id_db(post_id, db)

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this post"
        )

    to_update = form_data.model_dump(exclude_unset=True)

    updated_post = await update_post_db(to_update, post, db)

    return updated_post


async def delete_post_service(post_id: UUID, db: AsyncSession, current_user: User):
    post = await get_post_by_id_db(post_id, db)
    if current_user.id != post.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete this post as it's not yours",
        )

    await delete_post_db(current_user, post, db)


async def feed_post_service(db: AsyncSession):
    posts = await feed_post_db(db)

    return posts


async def delete_post_admin_service(post_id: UUID, db: AsyncSession):
    await delete_post_admin_db(post_id, db)
