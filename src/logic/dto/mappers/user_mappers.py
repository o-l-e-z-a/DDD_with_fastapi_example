from src.infrastructure.db.models.users import Users
from src.logic.dto.user_dto import UserDetailDTO


def user_to_detail_dto_mapper(user: Users) -> UserDetailDTO:
    return UserDetailDTO(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        telephone=user.telephone,
        is_admin=user.is_superuser,
        date_birthday=user.date_birthday,
    )
