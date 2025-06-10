import json
from http import HTTPStatus
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Query, Request, Response, HTTPException
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, add_pagination, paginate, Params

from models.AppStatus import AppStatus
from models.User import User, UserCreate, UserUpdate
app = FastAPI()
add_pagination(app)

users: list[User] = []

@app.get("/status", status_code=HTTPStatus.OK)
def status() -> AppStatus:
    return AppStatus(users=bool(users))

@app.get("/api/users/all", status_code=HTTPStatus.OK)
def get_all_users() -> list[User]:
    return users

@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    if user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    return users[user_id - 1]

@app.get("/api/users", status_code=HTTPStatus.OK)
def get_users(params: Params = Depends()) -> Page[User]:
    return paginate(users, params)

@app.post("/api/users", status_code=HTTPStatus.CREATED)
def create_user(user_create: UserCreate) -> User:
    new_id = len(users) + 1
    new_user = User(id=new_id, **user_create.model_dump())
    return new_user

@app.put("/api/users/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_update: UserUpdate, user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    updated_user = User(id=user_id, **user_update.model_dump())
    return updated_user

@app.delete("/api/users/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int) -> Response:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    return Response(status_code=204)

@app.exception_handler(HTTPException)
async def http_user_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"{exc.detail}"},
    )

if __name__ == "__main__":
    with open("users.json") as f:
        users = json.load(f)

    for user in users:
        User.model_validate(user)

    print("Users loaded")
    print(users)

    uvicorn.run(app, host="0.0.0.0", port=8000)