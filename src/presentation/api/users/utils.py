from datetime import UTC, datetime, timedelta

from jose import jwt

from src.presentation.api.settings import settings

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
ACCESS_TOKEN_COOKIE_FIELD = "access_token"
ACCESS_TOKEN_RESPONSE_FIELD = "access_token"
REFRESH_TOKEN_RESPONSE_FIELD = "refresh_token"


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, TOKEN_TYPE_FIELD: ACCESS_TOKEN_TYPE})
    encoded_jwt = jwt.encode(to_encode, settings.auth.SECRET_KEY, settings.auth.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, TOKEN_TYPE_FIELD: REFRESH_TOKEN_TYPE})
    encoded_jwt = jwt.encode(to_encode, settings.auth.SECRET_KEY, settings.auth.ALGORITHM)
    return encoded_jwt
