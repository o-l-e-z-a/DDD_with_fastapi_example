from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Response

from src.domain.users.entities import User
from src.logic.commands.user_commands import AddUserCommand, VerifyUserCredentialsCommand
from src.logic.exceptions.user_exceptions import IncorrectEmailOrPasswordLogicException, UserAlreadyExistsLogicException
from src.logic.mediator.base import Mediator
from src.presentation.api.dependencies import CurrentUser, get_current_user_for_refresh
from src.presentation.api.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from src.presentation.api.users.schema import AllUserSchema, UserCreateSchema, UserLoginSchema
from src.presentation.api.users.utils import (
    ACCESS_TOKEN_COOKIE_FIELD,
    ACCESS_TOKEN_RESPONSE_FIELD,
    REFRESH_TOKEN_RESPONSE_FIELD,
    create_access_token,
    create_refresh_token,
)

router_auth = APIRouter(route_class=DishkaRoute, prefix="/auth", tags=["auth"])
router_users = APIRouter(route_class=DishkaRoute, prefix="/users", tags=["Пользователи"])


@router_auth.post("/register/", status_code=201)
async def register_user(
    user_data: UserCreateSchema,
    mediator: FromDishka[Mediator],
):
    try:
        user: User = (await mediator.handle_command(AddUserCommand(**user_data.model_dump())))[0]
    except UserAlreadyExistsLogicException as err:
        raise UserAlreadyExistsException(err.title)
    return AllUserSchema.model_validate(user.to_dict())


@router_auth.post("/login/")
async def login_user(
    response: Response,
    user_data: UserLoginSchema,
    mediator: FromDishka[Mediator],
):
    try:
        user = (await mediator.handle_command(
            VerifyUserCredentialsCommand(**user_data.model_dump())
        ))[0]
    except IncorrectEmailOrPasswordLogicException as err:
        raise IncorrectEmailOrPasswordException(err.title)
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    response.set_cookie(ACCESS_TOKEN_COOKIE_FIELD, access_token, httponly=True)
    return {ACCESS_TOKEN_RESPONSE_FIELD: access_token, REFRESH_TOKEN_RESPONSE_FIELD: refresh_token}


@router_auth.post("/refresh/")
async def refresh(
    response: Response,
    user: User = Depends(get_current_user_for_refresh),
):
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(ACCESS_TOKEN_COOKIE_FIELD, access_token, httponly=True)
    return {ACCESS_TOKEN_RESPONSE_FIELD: access_token}


@router_auth.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(ACCESS_TOKEN_COOKIE_FIELD)


@router_users.get("/me/")
async def read_users_me(current_user: CurrentUser) -> AllUserSchema:
    return AllUserSchema.model_validate(current_user.to_dict())
