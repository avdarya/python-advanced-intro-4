from http import HTTPStatus

from fastapi import APIRouter

from app.database.engine import check_db_availability
from app.models.AppStatus import AppStatus
# from app.database import users_db

router = APIRouter()

@router.get("/status", status_code=HTTPStatus.OK)
def status() -> AppStatus:
    return AppStatus(database=check_db_availability())
