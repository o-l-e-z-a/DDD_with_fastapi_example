from datetime import UTC, datetime, timedelta
from typing import TypeAlias

from jose import ExpiredSignatureError, JWTError, jwt

from src.logic.dto.schedule_dto import MasterDetailDTO
from src.logic.dto.user_dto import UserDetailDTO
from src.logic.mediator.base import Mediator
from src.logic.queries.user_queries import GetUserByIdQuery
from src.presentation.api.exceptions import (
    IncorrectTokenFormatException,
    InvalidTokenType,
    TokenExpiredException,
    UserIsNotPresentException,
)
from src.presentation.api.settings import settings

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
ACCESS_TOKEN_COOKIE_FIELD = "access_token"
ACCESS_TOKEN_RESPONSE_FIELD = "access_token"
REFRESH_TOKEN_RESPONSE_FIELD = "refresh_token"

Token: TypeAlias = str
TokenPayload: TypeAlias = dict
CurrentUser: TypeAlias = UserDetailDTO
CurrentUserFromRefresh: TypeAlias = UserDetailDTO
CurrentMaster: TypeAlias = MasterDetailDTO
CurrentAdmin: TypeAlias = UserDetailDTO


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


def validate_token_type(payload: dict, token_type: str):
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type != token_type:
        raise InvalidTokenType
    return True


async def get_user_from_payload(user_id: str, mediator: Mediator) -> UserDetailDTO:
    user: UserDetailDTO | None = await mediator.handle_query(GetUserByIdQuery(user_id=int(user_id)))
    if not user:
        raise UserIsNotPresentException
    # elif not user.is_active:
    #     raise UserIsNotActiveException
    return user


async def get_current_user(
    mediator: Mediator,
    token: Token,
) -> UserDetailDTO:
    payload = get_token_payload(token)
    if validate_token_type(payload, ACCESS_TOKEN_TYPE):
        user_id = payload.get("sub")
        if not user_id:
            raise UserIsNotPresentException
        return await get_user_from_payload(user_id, mediator=mediator)


def get_token_payload(token: Token) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.auth.SECRET_KEY, settings.auth.ALGORITHM)
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException
    return payload
