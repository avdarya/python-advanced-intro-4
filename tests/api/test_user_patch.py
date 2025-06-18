import pytest
from typing import Callable, Any
from http import HTTPStatus

from app.models.User import UserUpdate
from clients.user_client import UserApiClient

def test_update_user(
        user_client: UserApiClient,
        user_payload_factory: Callable[[], dict[str, Any]],
        created_user: dict,
        created_user_cleanup: list[int]
):
    user_id = created_user["id"]
    user_obj_for_update = user_payload_factory()

    response = user_client.update_user_validated(user_id=user_id, user=UserUpdate(**user_obj_for_update))
    assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
    body = response.json()

    api_response = user_client.get_user(user_id=user_id)
    assert api_response.status_code == HTTPStatus.OK
    api_user = api_response.json()

    created_user_cleanup.append(user_id)

    assert "id" in body and isinstance(body["id"], int), f"Expected id: int = {body['id']}, but got {body['id']}"
    assert body["id"] == user_id, f"Expected id: {user_id}, but got {body['id']}"
    assert body["email"] == user_obj_for_update['email'], f"Expected email {user_obj_for_update['email']}, but got {body['email']}"
    assert body["first_name"] == user_obj_for_update['first_name'], f"Expected first_name {user_obj_for_update['first_name']}, but got {body['first_name']}"
    assert body["last_name"] == user_obj_for_update['last_name'], f"Expected last_name {user_obj_for_update['last_name']}, but got {body['last_name']}"
    assert body["avatar"] == user_obj_for_update['avatar'], f"Expected avatar {user_obj_for_update['avatar']}, but got {body['avatar']}"

    assert api_user["id"] == user_id, f"Expected id: {user_id}, but got {api_user['id']}"
    assert api_user["email"] == user_obj_for_update["email"], f"Expected email {user_obj_for_update['email']}, but got {api_user['email']}"
    assert api_user["first_name"] == user_obj_for_update["first_name"], f"Expected first_name {user_obj_for_update['first_name']}, but got {api_user['first_name']}"
    assert api_user["last_name"] == user_obj_for_update["last_name"], f"Expected last_name {user_obj_for_update['last_name']}, but got {api_user['last_name']}"
    assert api_user["avatar"] == user_obj_for_update["avatar"], f"Expected first_name {user_obj_for_update['avatar']}, but got {api_user['avatar']}"

@pytest.mark.parametrize("field", ["email", "first_name", "last_name", "avatar"])
def test_update_user_by_one_field(
        user_client: UserApiClient,
        created_user: dict,
        user_payload_factory: Callable[[], dict[str, Any]],
        created_user_cleanup: list[int],
        field: str
):
    user_id = created_user["id"]
    updated_field = user_payload_factory()[field]
    payload = {f"{field}": updated_field}

    response = user_client.update_user_validated(user_id=user_id, user=UserUpdate(**payload))
    assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
    body = response.json()

    created_user_cleanup.append(user_id)

    assert body["id"] == user_id, f"Expected id: {user_id}, but got {body['id']}"
    assert body[f"{field}"] == updated_field, f"Expected email {updated_field}, but got {body[f'{field}']}"

@pytest.mark.parametrize("err_msg", ["User not found"])
def test_update_not_existing_user(user_client: UserApiClient, created_user: dict, user_payload_factory: Callable[[], dict[str, Any]], err_msg: str):
    user_id = created_user["id"]
    updated_user = user_payload_factory()
    user_client.delete_user(user_id=user_id)
    response = user_client.update_user_validated(user_id=user_id, user=UserUpdate(**updated_user))
    assert response.status_code == HTTPStatus.NOT_FOUND, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    assert "message" in body, "Response body does not contain 'message' key"
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("email, err_msg", [
    ("", "invalid data"),
    ("libereddfo@@hotmail.edu", "invalid data"),
    ("janet.weaverreqres.in", "invalid data"),
    ("@reqres.in", "invalid data"),
    ("michael.lawson@reqres", "invalid data"),
    ("tracey.ramos@", "invalid data")
])
def test_update_user_invalid_email(user_client: UserApiClient, created_user: dict, created_user_cleanup: list[int], email: str, err_msg: str):
    user_id = created_user["id"]
    payload = {"email": email}
    response = user_client.update_user_raw(user_id=user_id, user=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    created_user_cleanup.append(user_id)
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("avatar_url, err_msg", [
    ("", "invalid data"),
    ("https://", "invalid data"),
    ("not-a-url", "invalid data"),
    ("www.example.com/avatar.jpg", "invalid data")
])
def test_update_user_invalid_avatar_url(user_client: UserApiClient, created_user: dict, created_user_cleanup: list[int], avatar_url: str, err_msg: str):
    user_id = created_user["id"]
    payload = {"avatar": avatar_url}
    response = user_client.update_user_raw(user_id=user_id, user=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    created_user_cleanup.append(user_id)
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("err_msg, invalid_id", [("Unprocessable Entity", 0), ("Unprocessable Entity", -1)])
def test_update_user_with_non_positive_id(user_client: UserApiClient, created_user: dict, created_user_cleanup: list[int], err_msg: str, invalid_id: int):
    user_id = created_user["id"]
    payload = {"last_name": "invalidid"}
    response = user_client.update_user_raw(user_id=invalid_id, user=payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    created_user_cleanup.append(user_id)
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("detail", ["Method Not Allowed"])
def test_update_user_invalid_method(user_client: UserApiClient, created_user: dict, created_user_cleanup: list[int], detail: str):
    user_id = created_user["id"]
    payload = {"last_name": "invalidmethod"}
    response = user_client.update_user_raw(user_id=user_id, user=payload, method="PUT")
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    created_user_cleanup.append(user_id)
    assert body["detail"] == detail, f"Expected detail {detail}, but got {body['detail']}"
