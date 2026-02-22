from uuid import UUID
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.repositories.user import (
    change_password_db,
    check_username_exist,
    create_user_db,
    delete_user_db,
    get_all_user,
    get_user_by_username,
    update_user_partial_db,
)
from app.schemas.user import ChangePassword, UserCreate, UserUpdate
from app.core.security import create_access_token, hash_password, verify_password


async def sign_in_service(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    user = await get_user_by_username(form_data.username, db)

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is not correct",
        )

    access_token = create_access_token({"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


async def sign_up_service(form_data: UserCreate, db: AsyncSession):
    stmt = select(User).where(User.username == form_data.username)

    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist"
        )

    hashed_pwd = hash_password(form_data.password)
    form_data.password = hashed_pwd

    data = form_data.model_dump()

    await create_user_db(data, db)

    return {"message": "Your account has been successfully created."}


# DB is included if in future is in need here
async def my_profile_service(db: AsyncSession, current_user: User):
    return current_user


async def update_profile_service(
    form_data: UserUpdate, db: AsyncSession, current_user: User
):
    if form_data.username:
        await check_username_exist(form_data.username, db)

    user = await get_user_by_username(current_user.username, db)

    data = form_data.model_dump(exclude_unset=True)

    user = await update_user_partial_db(data, user, db)

    return user


async def change_password_service(
    form_data: ChangePassword, db: AsyncSession, current_user: User
):
    if form_data.new_password != form_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="New password must match"
        )

    if form_data.current_password == form_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot have the same current password and new password",
        )

    if not verify_password(form_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is not correct"
        )

    hashed_pwd = hash_password(form_data.new_password)

    await change_password_db(hashed_pwd, current_user, db)

    return {"message": "You've successfully changed your password"}


async def delete_profile_service(password: str, db: AsyncSession, current_user: User):
    if not verify_password(password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password is not correct"
        )

    await delete_user_db(current_user, db)


# ADMIN
async def get_users_service(db: AsyncSession, current_user: User):
    users = await get_all_user(db)
    return users


async def delete_user_service(user_id: UUID, db: AsyncSession, current_user: User):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await delete_user_db(user, db)
