from datetime import datetime

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class UserData(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str

class SupportData(BaseModel):
    url: str
    text: str

class UserResponseModel(BaseModel):
    data: UserData
    support: SupportData

class CreateUserRequestModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    avatar: str

class CreateUserResponseModel(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str
    created_at: datetime
    updated_at: datetime

class UpdateUserRequestModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    avatar: str

class UpdateUserResponseModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    avatar: str
    updated_at: datetime

# "База данных" для демонстрации
fake_db = {
    2: {
            "id": 2,
            "first_name": "Naomi",
            "last_name": "Wall",
            "email": "libero@hotmail.edu",
            "avatar": "https://reqres.in/img/faces/2-image.jpg",
            "created_at": "2025-05-27T23:49:07.709984",
            "updated_at": "2025-05-27T23:49:07.709984",
    }
}

@app.get("/api/users/{user_id}", response_model=UserResponseModel)
def get_user(user_id: int) -> UserResponseModel:
    support_url = "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral"
    support_text = "Tired of writing endless social media content? Let Content Caddy generate it for you."
    mock_support_data = SupportData(url=support_url,text=support_text)

    user = fake_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = UserResponseModel(data=UserData(**user), support=mock_support_data)

    return result

@app.post("/api/users", response_model=CreateUserResponseModel, status_code=201)
def create_user(user: CreateUserRequestModel) -> CreateUserResponseModel:
    existing_emails = []
    for item in fake_db.values():
        existing_emails.append(item["email"])

    if any(
        user_email == user.email
        for user_email in existing_emails
    ):
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now()
    max_id = 0
    if len(fake_db.keys()) > 0:
        max_id = max(fake_db.keys())
    user_data = {
        "id": max_id + 1,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": user.avatar,
        "created_at": now,
        "updated_at": now
    }

    fake_db[user_data["id"]] = user_data

    return CreateUserResponseModel(**user_data)

@app.put("/api/users/{user_id}", response_model=UpdateUserResponseModel)
def update_user(user: UpdateUserRequestModel, user_id: int) -> UpdateUserResponseModel:
    existed_user = fake_db.get(user_id)
    if not existed_user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now()
    user_data = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": user.avatar,
        "updated_at": now,
        "created_at": existed_user["created_at"],
    }

    fake_db[user_id] = user_data

    return UpdateUserResponseModel(**user_data)

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int) -> Response:
    if not user_id in fake_db:
        raise HTTPException(status_code=404, detail="User not found")

    fake_db.pop(user_id)

    return Response(status_code=204)

@app.exception_handler(HTTPException)
async def http_user_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"{exc.detail}"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)