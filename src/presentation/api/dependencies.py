from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.presentation.api.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException, InvalidTokenType, UserIsNotAdminException, UserIsNotActiveException,
    UserIsNotMasterException,
)
from src.presentation.api.settings import settings
from src.presentation.api.users.utils import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, ACCESS_TOKEN_COOKIE_FIELD

http_bearer = HTTPBearer()


def get_token(request: Request) -> str:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_FIELD)
    if not token:
        raise TokenAbsentException
    return token


def get_token_payload(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError as e:
        raise IncorrectTokenFormatException
    return payload


# async def get_user_from_payload(session: DBSession, payload: dict) -> Users:
#     user_id: str = payload.get("sub")
#     if not user_id:
#         raise UserIsNotPresentException
#     user = await UserDAO(session).find_one_or_none(id=int(user_id))
#     if not user:
#         raise UserIsNotPresentException
#     elif not user.is_active:
#         raise UserIsNotActiveException
#     return user

