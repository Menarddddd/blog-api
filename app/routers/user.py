from typing import Annotated, List
from fastapi.routing import APIRouter
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password, verify_password


router = APIRouter()


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


@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(User).options(
            selectinload(User.posts),
            selectinload(User.refresh_tokens),
        )
    )
    users = result.scalars().all()

    return users


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def my_profile():
    pass
