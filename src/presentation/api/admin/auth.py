from typing import Optional

from dishka import make_async_container
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.infrastructure.db.provider import DBProvider
from src.logic.commands.user_commands import VerifyUserCredentialsCommand
from src.logic.mediator.base import Mediator
from src.logic.provider import LogicProvider
from src.presentation.api.settings import Settings, settings
from src.presentation.api.users.utils import create_access_token, get_current_user


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email: str = form["username"]  # type: ignore[assignment]
        password: str = form["password"]  # type: ignore[assignment]
        mediator = await container.get(Mediator)
        user = (await mediator.handle_command(VerifyUserCredentialsCommand(email=email, password=password)))[0]
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
        mediator = await container.get(Mediator)
        user = await get_current_user(mediator=mediator, token=token)
        if not user:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        return True


authentication_backend = AdminAuth(secret_key="...")
container = make_async_container(LogicProvider(), DBProvider(), context={Settings: settings})
