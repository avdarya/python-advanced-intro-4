import pytest
from http import HTTPStatus

from clients.user_client import UserApiClient

@pytest.mark.parametrize("err_msg", ["User not found"])
def test_delete_user(user_client: UserApiClient, created_user: dict, err_msg: str):
    user_id = created_user["id"]
    response = user_client.delete_user(user_id)
    assert response.status_code == HTTPStatus.NO_CONTENT, f"ERROR {response.status_code} {response.text}"

    api_deleted_user = user_client.get_user(user_id)
    assert api_deleted_user.status_code == HTTPStatus.NOT_FOUND
    assert api_deleted_user.json()["message"] == err_msg, f"Expected message {err_msg}, but got {api_deleted_user.json()}"

@pytest.mark.parametrize("err_msg", ["User not found"])
def test_delete_not_existing_user(user_client: UserApiClient, created_user: dict, err_msg: str):
    user_id = created_user["id"]
    user_client.delete_user(user_id)
    response = user_client.delete_user(user_id)
    assert response.status_code == HTTPStatus.NOT_FOUND, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body}"

@pytest.mark.parametrize("err_msg, invalid_id", [("Unprocessable Entity", 0), ("Unprocessable Entity", -1)])
def test_delete_user_with_non_positive_id(user_client: UserApiClient, err_msg: str, invalid_id: int):
    response = user_client.delete_user(invalid_id)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body}"

@pytest.mark.parametrize("err_msg, invalid_id", [("Unprocessable Entity", "id")])
def test_delete_user_with_invalid_id_type(user_client: UserApiClient, err_msg: str, invalid_id: str):
    response = user_client.delete_user(invalid_id)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"ERROR {response.status_code} {response.text}"