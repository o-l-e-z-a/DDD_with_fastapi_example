from fastapi import APIRouter, Response, Depends

from src.domain.users.entities import User
from src.logic.dto.user_dto import UserCreateDTO, UserLoginDTO
from src.logic.services.users_service import UserService
from src.presentation.api.dependencies import get_user_service, get_current_user_for_refresh, CurrentUser
from src.presentation.api.users.schema import UserCreateSchema, UserLoginSchema
from src.presentation.api.users.utils import create_access_token, create_refresh_token, ACCESS_TOKEN_COOKIE_FIELD

router_auth = APIRouter(prefix="/auth", tags=["auth"])
router_users = APIRouter(prefix="/users", tags=["Пользователи"])


@router_auth.post("/register/", status_code=201)
async def register_user(
        user_data: UserCreateSchema,
        user_service: UserService = Depends(get_user_service),
):
    await user_service.add_user(user_data=UserCreateDTO(**user_data.model_dump()))


@router_auth.post("/login/")
async def login_user(
        response: Response,
        user_data: UserLoginSchema,
        user_service: UserService = Depends(get_user_service),
):
    user = await user_service.check_login_and_verify_password(user_login_data=UserLoginDTO(**user_data.model_dump()))
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    response.set_cookie(ACCESS_TOKEN_COOKIE_FIELD, access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router_auth.post("/refresh/")
async def refresh(
        response: Response,
        user: User = Depends(get_current_user_for_refresh),
):
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(ACCESS_TOKEN_COOKIE_FIELD, access_token, httponly=True)
    return {"access_token": access_token}


@router_auth.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(ACCESS_TOKEN_COOKIE_FIELD)


@router_users.get("/me/")
async def read_users_me(current_user: CurrentUser):
    return current_user
