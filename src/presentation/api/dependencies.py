from dishka import Scope, provide
from dishka.integrations.fastapi import FastapiProvider
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.logic.mediator.base import Mediator
from src.logic.queries.schedule_queries import GetMasterByUserQuery
from src.presentation.api.exceptions import (
    TokenAbsentException,
    UserIsNotAdminException,
    UserIsNotMasterException,
    UserIsNotPresentException,
)
from src.presentation.api.users.utils import (
    ACCESS_TOKEN_COOKIE_FIELD,
    REFRESH_TOKEN_TYPE,
    CurrentAdmin,
    CurrentMaster,
    CurrentUser,
    CurrentUserFromRefresh,
    Token,
    get_current_user,
    get_token_payload,
    get_user_from_payload,
    validate_token_type,
)


class MyFastapiProvider(FastapiProvider):
    scope = Scope.REQUEST

    @provide()
    def get_http_bearer(self) -> HTTPBearer:
        return HTTPBearer()

    @provide()
    async def get_credentials(self, request: Request, http_bearer: HTTPBearer) -> HTTPAuthorizationCredentials:
        return await http_bearer(request)

    @provide()
    def get_token(self, request: Request) -> Token:
        token = request.cookies.get(ACCESS_TOKEN_COOKIE_FIELD)
        if not token:
            raise TokenAbsentException
        return token

    @provide()
    async def get_current_user(
        self,
        mediator: Mediator,
        token: Token,
    ) -> CurrentUser:
        return await get_current_user(mediator=mediator, token=token)

    @provide()
    async def get_current_master(
        self,
        user: CurrentUser,
        mediator: Mediator,
    ) -> CurrentMaster:
        master: CurrentMaster | None = await mediator.handle_query(GetMasterByUserQuery(user_id=user.id))
        if master:
            return master
        raise UserIsNotMasterException

    async def get_current_admin(self, user: CurrentUser) -> CurrentAdmin:
        if user.is_admin:
            return user
        raise UserIsNotAdminException

    async def get_current_user_for_refresh(
        self,
        mediator: Mediator,
        credentials: HTTPAuthorizationCredentials,
    ) -> CurrentUserFromRefresh:
        token = credentials.credentials
        payload = get_token_payload(token)
        if validate_token_type(payload, REFRESH_TOKEN_TYPE):
            user_id = payload.get("sub")
            if not user_id:
                raise UserIsNotPresentException
            return await get_user_from_payload(user_id, mediator=mediator)
