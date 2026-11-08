from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from .config import get_settings

password_hash = PasswordHash.recommended() # returns a configured hasher with sensible defaults

ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
        *, subject: str, expires_delta: timedelta | None = None
) -> str:
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": subject,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        get_settings().jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )