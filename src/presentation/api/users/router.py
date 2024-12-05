from fastapi import APIRouter, Response, Depends

from src.presentation.api.users.schema import UserCreateSchema

router_auth = APIRouter(prefix="/auth", tags=["auth"])
router_users = APIRouter(prefix="/users", tags=["Пользователи"])


# @router_auth.post("/register/", status_code=201)
# async def register_user(
#         user_data: UserCreateSchema,
#         user_dao: UserDAO = Depends(get_user_dao),
#         user_point_dao: UserPointDAO = Depends(get_user_point_dao)
# ):
#     existing_user = await user_dao.find_duplicate_user(email=user_data.email, telephone=user_data.telephone)
#     if existing_user:
#         raise UserAlreadyExistsException
#     password = get_password_hash(user_data.password)
#     new_user_id = await user_dao.add(
#         email=user_data.email,
#         first_name=user_data.first_name,
#         last_name=user_data.last_name,
#         telephone=user_data.telephone,
#         date_birthday=user_data.date_birthday,
#         hashed_password=password
#     )
#     await user_point_dao.add(user_id=new_user_id)


# @router_auth.post("/login/")
# async def login_user(
#         response: Response,
#         user_data: UserLoginSchema,
#         user_dao: UserDAO = Depends(get_user_dao),
# ):
#     user = await authenticate_user(user_dao, user_data.email, user_data.password)
#     access_token = create_access_token({"sub": str(user.id)})
#     refresh_token = create_refresh_token({"sub": str(user.id)})
#     response.set_cookie(ACCESS_TOKEN_COOKIE_FIELD, access_token, httponly=True)
#     return {"access_token": access_token, "refresh_token": refresh_token}


# @router_auth.post("/refresh/")
# async def refresh(
#         response: Response,
#         user: Users = Depends(get_current_user_for_refresh),
# ):
#     access_token = create_access_token({"sub": str(user.id)})
#     response.set_cookie(ACCESS_TOKEN_COOKIE_FIELD, access_token, httponly=True)
#     return {"access_token": access_token}
#
#
# @router_auth.post("/logout/")
# async def logout_user(response: Response):
#     response.delete_cookie(ACCESS_TOKEN_COOKIE_FIELD)
#
#
# @router_users.get("/me/")
# async def read_users_me(current_user: CurrentUser):
#     return current_user

