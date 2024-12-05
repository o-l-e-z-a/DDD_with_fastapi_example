from fastapi import APIRouter, Response, Depends


router_auth = APIRouter(prefix="/auth", tags=["auth"])
router_users = APIRouter(prefix="/users", tags=["Пользователи"])

