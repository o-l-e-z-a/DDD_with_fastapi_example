from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from src.domain.schedules.entities import Master
from src.domain.users.entities import User
from src.infrastructure.db.config import get_async_engine, get_async_session_factory
from src.logic.mediator.base import Mediator
from src.logic.queries.schedule_queries import GetMasterByUserQuery
from src.logic.queries.user_queries import GetUserByIdQuery
from src.logic.services.order_service import PromotionService
from src.logic.services.schedule_service import OrderService
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.presentation.api.exceptions import (
    IncorrectTokenFormatException,
    InvalidTokenType,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotAdminException,
    UserIsNotMasterException,
    UserIsNotPresentException,
)
from src.presentation.api.settings import settings
from src.presentation.api.users.utils import (
    ACCESS_TOKEN_COOKIE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
)

http_bearer = HTTPBearer()


def get_token(request: Request) -> str:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_FIELD)
    if not token:
        raise TokenAbsentException
    return token


def get_token_payload(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.auth.SECRET_KEY, settings.auth.ALGORITHM)
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException
    return payload


def get_async_session_maker():
    engine = get_async_engine(settings)
    return get_async_session_factory(engine)


def get_sqla_user_uow(async_session_maker=Depends(get_async_session_maker)) -> SQLAlchemyUsersUnitOfWork:
    uow = SQLAlchemyUsersUnitOfWork(session_factory=async_session_maker)
    return uow


def get_sqla_schedule_uow(async_session_maker=Depends(get_async_session_maker)) -> SQLAlchemyScheduleUnitOfWork:
    uow = SQLAlchemyScheduleUnitOfWork(session_factory=async_session_maker)
    return uow


def get_sqla_order_uow(async_session_maker=Depends(get_async_session_maker)) -> SQLAlchemyOrderUnitOfWork:
    uow = SQLAlchemyOrderUnitOfWork(session_factory=async_session_maker)
    return uow


def get_order_service(sql_user_uow: SQLAlchemyOrderUnitOfWork = Depends(get_sqla_order_uow)) -> OrderService:
    return OrderService(sql_user_uow)


def get_promotion_service(sql_user_uow: SQLAlchemyOrderUnitOfWork = Depends(get_sqla_order_uow)) -> PromotionService:
    return PromotionService(sql_user_uow)


async def get_user_from_payload(
    user_id: str,
    mediator: Mediator
) -> User:
    user = await mediator.handle_query(GetUserByIdQuery(user_id=int(user_id)))
    if not user:
        raise UserIsNotPresentException
    # elif not user.is_active:
    #     raise UserIsNotActiveException
    return user


async def get_current_user(
    mediator: FromDishka[Mediator],
    token: str = Depends(get_token),
) -> User:
    payload = get_token_payload(token)
    if validate_token_type(payload, ACCESS_TOKEN_TYPE):
        user_id = payload.get("sub")
        if not user_id:
            raise UserIsNotPresentException
        return await get_user_from_payload(user_id, mediator=mediator)


async def get_current_user_for_refresh(
    mediator: FromDishka[Mediator],
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> User:
    token = credentials.credentials
    payload = get_token_payload(token)
    if validate_token_type(payload, REFRESH_TOKEN_TYPE):
        user_id = payload.get("sub")
        if not user_id:
            raise UserIsNotPresentException
        return await get_user_from_payload(user_id, mediator=mediator)


def validate_token_type(payload: dict, token_type: str):
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type != token_type:
        raise InvalidTokenType
    return True


CurrentUser = Annotated[User, Depends(get_current_user)]


@inject
async def get_current_master(
    user: CurrentUser,
    mediator: FromDishka[Mediator],
) -> Master:
    master = await mediator.handle_query(GetMasterByUserQuery(user_id=user.id))
    if master:
        return master
    raise UserIsNotMasterException


CurrentMaster = Annotated[Master, Depends(get_current_master)]


async def get_current_admin(user: CurrentUser) -> User:
    if user.is_admin:
        return user
    raise UserIsNotAdminException


CurrentAdmin = Annotated[User, Depends(get_current_admin)]
