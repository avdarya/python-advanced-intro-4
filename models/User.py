from pydantic import BaseModel, EmailStr, HttpUrl

class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl

class UserUpdate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl