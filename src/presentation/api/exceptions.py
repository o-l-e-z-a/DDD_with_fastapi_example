from fastapi import HTTPException, status

EXCEPTION_DETAIL_FIELD = "detail"


class BaseApiException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = ""

    def __init__(self, detail: str | None = None):
        detail = detail if detail else self.detail
        super().__init__(status_code=self.status_code, detail=detail)


class UserAlreadyExistsException(BaseApiException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class TokenAbsentException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class InvalidTokenType(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный тип токена"


class UserIsNotPresentException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь не создан"


class UserIsNotActiveException(BaseApiException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Ваша учетная запись заблокирована"


class UserIsNotAdminException(BaseApiException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "У пользователя нету прав администратора"


class UserIsNotMasterException(BaseApiException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Пользователь не является мастером"


class NotUserOrderException(BaseApiException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Пользователь не может редактировать чужой заказ"


class CannotAddDataToDatabase(BaseApiException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Не удалось добавить запись"


class CannotUpdateDataToDatabase(BaseApiException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Не удалось добавить запись"


class NotFoundHTTPException(BaseApiException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Запись не найдена"


class NotCorrectDataHTTPException(BaseApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Переданные данные не корректны"
