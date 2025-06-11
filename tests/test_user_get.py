from http import HTTPStatus

import pytest
import requests

from jsonschema import validate

from app.models.User import User
from schemas.single_user_schema import single_user

def test_user(app_url, fill_test_data):
    for user_id in (fill_test_data[0], fill_test_data[-1]):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK, f"Expected status code 200, but got {response.status_code}"
        user = response.json()
        User.model_validate(user)

def test_user_data(app_url, created_user, created_user_cleanup):
    user_id = created_user["id"]
    response = requests.get(f"{app_url}/api/users/{user_id}")
    body = response.json()
    created_user_cleanup.append(user_id)
    assert response.status_code == 200
    assert body["id"] == user_id, f"Expected first_name {user_id}, but got {body['id']}"
    assert body["first_name"] == created_user['first_name'], f"Expected first_name {created_user['first_name']}, but got {body['first_name']}"
    assert body["last_name"] == created_user['last_name'], f"Expected last_name {created_user['last_name']}, but got {body['last_name']}"
    assert body["email"] == created_user['email'], f"Expected email {created_user['email']}, but got {body['email']}"
    assert body["avatar"] == created_user['avatar'], f"Expected avatar {created_user['avatar']}, but got {body['avatar']}"


def test_single_user_schema_validate_from_file(app_url, created_user, created_user_cleanup):
    user_id = created_user["id"]
    response = requests.get(f"{app_url}/api/users/{user_id}")
    body = response.json()
    created_user_cleanup.append(user_id)
    assert response.status_code == HTTPStatus.OK
    validate(body, schema=single_user)

@pytest.mark.parametrize("err_msg", ["User not found"])
def test_get_not_existing_user(app_url, created_user, err_msg):
    user_id = created_user["id"]
    requests.delete(f"{app_url}/api/users/{user_id}")
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    body = response.json()
    assert response.status_code == HTTPStatus.NOT_FOUND, f"Expected status code 404, but got {response.status_code}"
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("user_id", [-1, 0, "hello"])
def test_user_invalid_value(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY







