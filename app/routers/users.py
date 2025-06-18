from http import HTTPStatus
from typing import Iterable
from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Depends
from fastapi_pagination import Page, paginate, Params

from app.database import users
from app.models.User import User, UserCreate, UserUpdate

router = APIRouter(prefix="/api/users")

@router.get("/all", status_code=HTTPStatus.OK)
def get_all_users() -> Iterable[User]:
    return users.get_users()

@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")

    user = users.get_user(user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    return user

@router.get("/", status_code=HTTPStatus.OK, response_model=Page[User])
def get_users(params: Params = Depends()) -> Iterable[User]:
    return paginate(users.get_users(), params)

@router.post("/", status_code=HTTPStatus.CREATED)
def create_user(user_create: User) -> User:
    UserCreate.model_validate(user_create.model_dump())
    return users.create_user(user_create)

@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_update: User, user_id: int) -> type[User]:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    UserUpdate.model_validate(user_update.model_dump())
    return users.update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int) -> Response:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    users.delete_user(user_id)
    return Response(status_code=204)
