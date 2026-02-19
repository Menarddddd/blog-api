from uuid import UUID
from typing import Annotated, List
from fastapi.routing import APIRouter
from fastapi import status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import Role, User
from app.repositories.user import (
    get_current_user,
    required_role,
)
from app.schemas.user import ChangePassword, Token, UserCreate, UserResponse, UserUpdate
from app.services.user import (
    change_password_service,
    delete_profile_service,
    delete_user_service,
    get_users_service,
    my_profile_service,
    sign_in_service,
    sign_up_service,
    update_profile_service,
)


router = APIRouter()


@router.post("/signIn", response_model=Token, status_code=status.HTTP_200_OK)
async def sign_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await sign_in_service(form_data, db)
    return result


@router.post("/signUp", status_code=status.HTTP_201_CREATED)
async def sign_up(form_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await sign_up_service(form_data, db)
    return result


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await my_profile_service(db, current_user)


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    form_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await update_profile_service(form_data, db, current_user)
    return result


@router.post("/me", status_code=status.HTTP_200_OK)
async def change_password(
    form_data: ChangePassword,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await change_password_service(form_data, db, current_user)
    return result


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    password: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_profile_service(password, db, current_user)


# ADMIN PROTECTED ROUTE
@router.get("/admin", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(required_role(Role.ADMIN))],
):
    result = await get_users_service(db, current_user)
    return result


@router.delete("/admin", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(required_role(Role.ADMIN))],
):
    result = await delete_user_service(user_id, db, current_user)
