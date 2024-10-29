from fastapi import HTTPException, status


class BaseException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = ""

    def __init__(self, detail: str | None = None):
        detail = detail if detail else self.detail
        super().__init__(status_code=self.status_code, detail=detail)


class UserAlreadyExistsException(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class TokenAbsentException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class InvalidTokenType(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный тип токена"


class UserIsNotPresentException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь не создан"


class UserIsNotActiveException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Ваша учетная запись заблокирована"


class UserIsNotAdminException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "У пользователя нету прав администратора"


class UserIsNotMasterException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Пользователь не является мастером"


class CannotAddDataToDatabase(BaseException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Не удалось добавить запись"


class BaseNotFound(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    object_name = ""

    def __init__(self):
        detail = f"Не удалось найти {self.object_name} с данным id"
        super().__init__(status_code=self.status_code, detail=detail)


class ScheduleNotFound(BaseNotFound):
    object_name = "расписание"


class OrderNotFound(BaseNotFound):
    object_name = "заказ"


class PromotionNotFound(BaseNotFound):
    object_name = "промокод"


class ServiceNotFound(BaseNotFound):
    object_name = "сервис"


class InventoryNotFound(BaseNotFound):
    object_name = "инвентарь"
