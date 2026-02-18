import jwt
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta

from app.core.settings import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# TOKEN


def create_access_token(sub: dict):
    to_encode = sub.copy()
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_EXPIRE_MINUTES
    )
    to_encode["exp"] = expire_at

    access_token = jwt.encode(
        to_encode,
        settings.ACCESS_SECRET_KEY.get_secret_value(),
        algorithm=settings.ALGORITHM,
    )

    return access_token
