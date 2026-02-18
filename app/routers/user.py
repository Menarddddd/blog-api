from uuid import UUID
from typing import Annotated, List
from fastapi.routing import APIRouter
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import Role, User
from app.repositories.user import check_username_exist, get_current_user, required_role
from app.schemas.user import ChangePassword, Token, UserCreate, UserResponse, UserUpdate
from app.core.security import create_access_token, hash_password, verify_password


router = APIRouter()


@router.post("/signIn", response_model=Token, status_code=status.HTTP_200_OK)
async def sign_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Username not found"
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is not correct",
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = ""
    # save the refresh token here

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/signUp", status_code=status.HTTP_201_CREATED)
async def sign_up(form_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
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
    new_user = User(**data)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Your account has been successfully created."}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    form_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if form_data.username:
        await check_username_exist(form_data.username, db)

    result = await db.execute(
        select(User)
        .options(selectinload(User.posts), selectinload(User.refresh_tokens))
        .where(User.username == current_user.username)
    )
    user = result.scalars().first()

    data = form_data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/me", status_code=status.HTTP_200_OK)
async def change_password(
    form_data: ChangePassword,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if form_data.new_password != form_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="New password must match"
        )

    if not verify_password(form_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is not correct"
        )

    hashed_pwd = hash_password(form_data.new_password)

    current_user.password = hashed_pwd

    await db.commit()
    await db.refresh(current_user)

    return {"message": "You've successfully changed your password"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    password: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not verify_password(password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password is not correct"
        )

    await db.delete(current_user)
    await db.commit()


# FIX THIS LATER
# ADMIN PROTECTED ROUTE
@router.get("/admin", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(required_role(Role.ADMIN))],
):
    result = await db.execute(
        select(User).options(
            selectinload(User.posts),
            selectinload(User.refresh_tokens),
        )
    )
    users = result.scalars().all()

    return users


@router.delete("/admin", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(required_role(Role.ADMIN))],
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    await db.delete(user)
    await db.commit()
