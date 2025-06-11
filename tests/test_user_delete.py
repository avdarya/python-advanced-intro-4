from http import HTTPStatus

import pytest
import requests

def test_delete_user(app_url, created_user):
    user_id = created_user["id"]
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, f"Expected status code 204, but got {response.status_code}"

@pytest.mark.parametrize("err_msg", ["User not found"])
def test_delete_not_existing_user(app_url, created_user, err_msg):
    user_id = created_user["id"]
    requests.delete(f"{app_url}/api/users/{user_id}")
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    body = response.json()
    assert response.status_code == HTTPStatus.NOT_FOUND, f"Expected status code 404, but got {response.status_code}"
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("err_msg, invalid_id", [("Unprocessable Entity", 0), ("Unprocessable Entity", -1)])
def test_delete_user_invalid_user_id(app_url, created_user, created_user_cleanup, err_msg, invalid_id):
    user_id = created_user["id"]
    response = requests.delete(f"{app_url}/api/users/{invalid_id}")
    created_user_cleanup.append(user_id)
    body = response.json()
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status code 422, but got {response.status_code}"
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"
