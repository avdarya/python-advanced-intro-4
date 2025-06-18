import pytest
from http import HTTPStatus

from app.models.User import User
from clients.user_client import UserApiClient

@pytest.mark.usefixtures("fill_test_data")
def test_users(user_client: UserApiClient):
    response = user_client.get_users()
    assert response.status_code == HTTPStatus.OK
    user_list = response.json()["items"]
    for user in user_list:
        User.model_validate(user)

@pytest.mark.usefixtures("fill_test_data")
def test_user_no_duplicates(all_users: list):
    user_ids = [user["id"] for user in all_users]
    assert len(user_ids) == len(set(user_ids))