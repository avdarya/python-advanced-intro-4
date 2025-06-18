from typing import Iterable, Type, Sequence

from fastapi import HTTPException
from sqlmodel import Session, select
from .engine import engine
from ..models.User import User, UserCreate


def get_user(user_id: int) -> User | None:
    with Session(engine) as session:
        return session.get(User, user_id)

def get_users() -> Sequence[User]:
    with Session(engine) as session:
        statement = select(User)
        return session.exec(statement).all()

def create_user(user: UserCreate) -> User:
    new_user = User(**user.model_dump(mode="json"))
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

def update_user(user_id: int, user: User) -> User:
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()