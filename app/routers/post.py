from uuid import UUID
from typing import Annotated, List
from fastapi.routing import APIRouter
from fastapi import status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.repositories.user import get_current_user
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.post import (
    create_post_service,
    delete_post_service,
    get_post_service,
    my_posts_service,
    update_post_service,
)


router = APIRouter()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    form_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    post = await create_post_service(form_data, db, current_user)

    return post


@router.get("", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
async def my_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    posts = await my_posts_service(db, current_user)

    return posts


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    post = await get_post_service(post_id, db, current_user)

    return post


@router.patch("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def update_post(
    form_data: PostUpdate,
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    updated_post = await update_post_service(form_data, post_id, db, current_user)

    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_post_service(post_id, db, current_user)
