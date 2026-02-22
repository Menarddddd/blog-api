import uuid
import jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.core.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import Role, User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/signIn")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
        )
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = uuid.UUID(sub)

    except (jwt.PyJWKError, jwt.InvalidSignatureError, jwt.ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User)
        .options(
            selectinload(User.posts).options(
                selectinload(Post.comments).options(selectinload(Comment.author))
            ),
            selectinload(User.comments),
        )
        .where(User.id == user_id)
    )

    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def check_username_exist(username: str, db: AsyncSession):
    stmt = select(User).where(User.username == username)

    result = await db.execute(stmt)

    user = result.scalars().first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist"
        )


def required_role(role: Role):
    def role_checker(current_user: Annotated[User, Depends(get_current_user)]):
        if role != current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This route requires admin account",
            )
        return current_user

    return role_checker


async def get_user_by_username(username: str, db):
    stmt = (
        select(User)
        .options(
            selectinload(User.posts),
            selectinload(User.comments),
        )
        .where(User.username == username)
    )

    result = await db.execute(stmt)

    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Username not found"
        )

    return user


async def create_user_db(form_data: dict, db: AsyncSession):
    new_user = User(**form_data)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)


async def update_user_partial_db(form_data: dict, user: User, db: AsyncSession):
    for key, value in form_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user


async def change_password_db(hashed_pwd: str, user: User, db: AsyncSession):
    user.password = hashed_pwd

    await db.commit()
    await db.refresh(user)


async def delete_user_db(user: User, db: AsyncSession):
    await db.delete(user)
    await db.commit()


# ADMIN
async def get_all_user(db: AsyncSession):
    result = await db.execute(
        select(User).options(
            selectinload(User.posts).options(selectinload(Post.comments)),
            selectinload(User.comments),
        )
    )
    users = result.scalars().all()

    return users
