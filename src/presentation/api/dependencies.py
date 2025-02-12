from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from src.domain.schedules.entities import Master
from src.domain.users.entities import User
from src.infrastructure.db.config import get_async_engine, get_async_session_factory
from src.logic.services.order_service import PromotionService
from src.logic.services.schedule_service import MasterService, ProcedureService, ScheduleService, OrderService
from src.logic.services.users_service import UserService
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork
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
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
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


def get_user_service(sql_user_uow: SQLAlchemyUsersUnitOfWork = Depends(get_sqla_user_uow)) -> UserService:
    return UserService(sql_user_uow)


def get_schedule_service(
    sql_user_uow: SQLAlchemyScheduleUnitOfWork = Depends(get_sqla_schedule_uow),
) -> ScheduleService:
    return ScheduleService(sql_user_uow)


def get_procedure_service(
    sql_user_uow: SQLAlchemyScheduleUnitOfWork = Depends(get_sqla_schedule_uow),
) -> ProcedureService:
    return ProcedureService(sql_user_uow)


def get_order_service(sql_user_uow: SQLAlchemyOrderUnitOfWork = Depends(get_sqla_order_uow)) -> OrderService:
    return OrderService(sql_user_uow)


def get_promotion_service(sql_user_uow: SQLAlchemyOrderUnitOfWork = Depends(get_sqla_order_uow)) -> PromotionService:
    return PromotionService(sql_user_uow)


def get_master_service(sql_user_uow: SQLAlchemyScheduleUnitOfWork = Depends(get_sqla_schedule_uow)) -> MasterService:
    return MasterService(sql_user_uow)


async def get_user_from_payload(payload: dict, user_service: UserService) -> User:
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await user_service.get_user_by_id(user_id=int(user_id))
    if not user:
        raise UserIsNotPresentException
    # elif not user.is_active:
    #     raise UserIsNotActiveException
    return user


async def get_current_user(
    token: str = Depends(get_token), user_service: UserService = Depends(get_user_service)
) -> User:
    payload = get_token_payload(token)
    if validate_token_type(payload, ACCESS_TOKEN_TYPE):
        return await get_user_from_payload(payload=payload, user_service=user_service)


async def get_current_user_for_refresh(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    user_service: UserService = Depends(get_user_service),
) -> User:
    token = credentials.credentials
    payload = get_token_payload(token)
    if validate_token_type(payload, REFRESH_TOKEN_TYPE):
        return await get_user_from_payload(payload=payload, user_service=user_service)


def validate_token_type(payload: dict, token_type: str):
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type != token_type:
        raise InvalidTokenType
    return True


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_master(user: CurrentUser, master_service: MasterService = Depends(get_master_service)) -> Master:
    master = await master_service.get_master_by_user(user=user)
    if master:
        return master
    raise UserIsNotMasterException


CurrentMaster = Annotated[Master, Depends(get_current_master)]


async def get_current_admin(user: CurrentUser) -> User:
    if user.is_admin:
        return user
    raise UserIsNotAdminException


CurrentAdmin = Annotated[User, Depends(get_current_admin)]
