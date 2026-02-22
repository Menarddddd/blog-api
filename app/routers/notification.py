from uuid import UUID
from typing import Annotated, List
from fastapi.routing import APIRouter
from fastapi import status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.repositories.user import get_current_user
from app.schemas.notification import NotificationResponse
from app.services.notification import (
    clear_notifications_service,
    delete_notification_service,
    get_notification_service,
    my_notifications_service,
)


router = APIRouter()


@router.get(
    "", response_model=List[NotificationResponse], status_code=status.HTTP_200_OK
)
async def my_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    notifications = await my_notifications_service(db, current_user)

    return notifications


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await clear_notifications_service(db, current_user)


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_notification(
    notification_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    notification = await get_notification_service(notification_id, db, current_user)

    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_notification_service(notification_id, db)
