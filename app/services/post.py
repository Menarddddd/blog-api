from uuid import UUID
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.post import Post
from app.models.user import User
from app.repositories.post import (
    create_post_db,
    delete_post_db,
    get_all_post_db,
    get_post_by_id_db,
    update_post_db,
)
from app.repositories.user import get_current_user
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
    posts = await get_all_post_db(db)

    return posts


async def get_post_service(post_id: UUID, db: AsyncSession, current_user: User):
    post = await get_post_by_id_db(post_id, db)

    return post


async def update_post_service(
    form_data: PostUpdate,
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    post = await get_post_by_id_db(post_id, db)

    to_update = form_data.model_dump(exclude_unset=True)

    updated_post = await update_post_db(to_update, post, db)

    return updated_post


async def delete_post_service(post_id: UUID, db: AsyncSession, current_user: User):
    await delete_post_db(post_id, db)
