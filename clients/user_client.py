from typing import Any

from requests import Response

from config import Server
from settings import PaginationSettings
from utils.base_session import BaseSession
from app.models.User import UserCreate, UserUpdate

pagination_config = PaginationSettings()

class UserApiClient:
    def __init__(self, env: str) -> None:
        self.session = BaseSession(base_url=Server(env).base_url)

    def get_user(self, user_id: Any) -> Response:
        return self.session.get(f"/api/users/{user_id}")

    def get_users(
            self,
            page: Any = pagination_config.default_page,
            size: Any = pagination_config.default_size
    ) -> Response:
        return self.session.get(f"/api/users", params={"page": page, "size": size})

    def get_all_users(self) -> Response:
        return self.session.get(f"/api/users/all")

    def create_user_validated(self, user: UserCreate) -> Response:
       return self.session.post(f"/api/users", json=user.model_dump(mode="json"))

    def create_user_raw(self, user: dict, method: str = "POST") -> Response:
        return self.session.request(method=method, path=f"/api/users", json=user)

    def update_user_validated(self, user_id: int, user: UserUpdate) -> Response:
        return self.session.patch(f"/api/users/{user_id}", json=user.model_dump(mode="json", exclude_none=True))

    def update_user_raw(self, user_id: Any, user:dict, method: str = "PATCH") -> Response:
        return self.session.request(method, path=f"/api/users/{user_id}", json=user)

    def delete_user(self, user_id: Any) -> Response:
        return self.session.delete(f"/api/users/{user_id}")


