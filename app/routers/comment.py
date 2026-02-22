from uuid import UUID
from typing import Annotated, List
from fastapi.routing import APIRouter
from fastapi import status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import Role, User
from app.repositories.user import get_current_user, required_role
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment import (
    create_comment_service,
    delete_comment_admin_service,
    delete_comment_service,
    get_comment_service,
    get_comments_admin_service,
    my_comments_service,
    update_comment_service,
)

router = APIRouter()


# ADMIN
@router.get(
    "/admin", response_model=List[CommentResponse], status_code=status.HTTP_200_OK
)
async def get_comments_admin(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(required_role(Role.ADMIN))],
):
    comments = await get_comments_admin_service(db)
    return comments


@router.delete("/admin/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_admin(
    comment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(required_role(Role.ADMIN))],
):
    await delete_comment_admin_service(comment_id, db)


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    form_data: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    loaded_comment = await create_comment_service(post_id, form_data, db, current_user)
    return loaded_comment


@router.get(
    "/my_comments", response_model=List[CommentResponse], status_code=status.HTTP_200_OK
)
async def my_comments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    comments = await my_comments_service(db, current_user)

    return comments


@router.get(
    "/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK
)
async def get_comment(
    comment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    comment = await get_comment_service(comment_id, db)

    return comment


@router.patch(
    "/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK
)
async def update_comment(
    form_data: CommentUpdate,
    comment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    updated_comment = await update_comment_service(
        form_data, comment_id, db, current_user
    )

    return updated_comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_comment_service(current_user, comment_id, db)
