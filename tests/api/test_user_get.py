import pytest

from http import HTTPStatus
from jsonschema import validate

from app.models.User import User
from clients.user_client import UserApiClient
from schemas.single_user_schema import single_user

def test_user_data(user_client: UserApiClient, created_user: dict, created_user_cleanup: list[int]):
    user_id = created_user["id"]
    response = user_client.get_user(user_id)
    assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
    body = response.json()

    created_user_cleanup.append(user_id)

    assert body["id"] == user_id, f"Expected user id {user_id}, but got {body['id']}"
    assert body["first_name"] == created_user['first_name'], f"Expected first_name {created_user['first_name']}, but got {body['first_name']}"
    assert body["last_name"] == created_user['last_name'], f"Expected last_name {created_user['last_name']}, but got {body['last_name']}"
    assert body["email"] == created_user['email'], f"Expected email {created_user['email']}, but got {body['email']}"
    assert body["avatar"] == created_user['avatar'], f"Expected avatar {created_user['avatar']}, but got {body['avatar']}"

def test_user_model(user_client: UserApiClient, fill_test_data: list[int]):
    for user_id in (fill_test_data[0], fill_test_data[-1]):
        response = user_client.get_user(user_id)
        assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
        user = response.json()
        User.model_validate(user)

def test_single_user_schema_validate_from_file(user_client: UserApiClient, created_user: dict, created_user_cleanup: list[int]):
    user_id = created_user["id"]
    response = user_client.get_user(user_id)
    assert response.status_code == HTTPStatus.OK
    body = response.json()

    created_user_cleanup.append(user_id)

    validate(body, schema=single_user)

@pytest.mark.parametrize("err_msg", ["User not found"])
def test_get_not_existing_user(user_client: UserApiClient, created_user: dict, err_msg: str):
    user_id = created_user["id"]
    user_client.delete_user(user_id)
    response = user_client.get_user(user_id)
    assert response.status_code == HTTPStatus.NOT_FOUND, f"ERROR {response.status_code} {response.text}"

    body = response.json()

    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("user_id, err_msg", [(-1, "Invalid user id"), (0, "Invalid user id")])
def test_get_user_with_non_positive_id(user_client: UserApiClient, user_id: int, err_msg: str):
    response = user_client.get_user(user_id)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body}"