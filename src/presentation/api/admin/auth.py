from typing import Optional

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.logic.dto.user_dto import UserLoginDTO
from src.logic.services.users_service import UserService
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.presentation.api.dependencies import get_current_user
from src.presentation.api.users.utils import create_access_token


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
        sql_user_uow = SQLAlchemyUsersUnitOfWork()
        user_service = UserService(sql_user_uow)
        user = await user_service.check_login_and_verify_password(
            user_login_data=UserLoginDTO(email=email, password=password)
        )
        if user:
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse] | bool:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        sql_user_uow = SQLAlchemyUsersUnitOfWork()
        user_service = UserService(sql_user_uow)
        user = await get_current_user(user_service=user_service, token=token)
        if not user:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        return True


authentication_backend = AdminAuth(secret_key="...")
