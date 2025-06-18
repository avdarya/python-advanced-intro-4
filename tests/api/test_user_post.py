from typing import Callable, Any

import pytest
from http import HTTPStatus

from app.models.User import UserCreate
from clients.user_client import UserApiClient

def test_create_user(
        user_client: UserApiClient,
        user_payload_factory: Callable[[],
        dict[str, Any]],
        created_user_cleanup: list[int]
):
    user = user_payload_factory()
    user_obj = UserCreate(**user)

    response = user_client.create_user_validated(user=user_obj)
    assert response.status_code == HTTPStatus.CREATED, f"ERROR {response.status_code} {response.text}"
    body = response.json()

    api_response = user_client.get_user(user_id=body["id"])
    assert api_response.status_code == HTTPStatus.OK
    api_user = api_response.json()

    created_user_cleanup.append(body["id"])

    assert "id" in body and isinstance(body["id"], int), f"Expected id: int = {body['id']}, but got {body['id']}"
    assert body["email"] == user["email"], f"Expected email {user['email']}, but got {body['email']}"
    assert body["first_name"] == user["first_name"], f"Expected first_name {user['first_name']}, but got {body['first_name']}"
    assert body["last_name"] == user["last_name"], f"Expected last_name {user['last_name']}, but got {body['last_name']}"
    assert body["avatar"] == user["avatar"], f"Expected avatar {user['avatar']}, but got {body['avatar']}"

    assert api_user["id"] == body["id"]
    assert api_user["email"] == user["email"]
    assert api_user["first_name"] == user["first_name"]
    assert api_user["last_name"] == user["last_name"]
    assert api_user["avatar"] == user["avatar"]

@pytest.mark.parametrize("email", [
    "",
    None,
    "libereddfo@@hotmail.edu",
    "janet.weaverreqres.in",
    "@reqres.in",
    "michael.lawson@reqres",
    "tracey.ramos@"
])
def test_create_user_invalid_email(user_client: UserApiClient, email: Any):
    payload = {
        "email": email,
        "first_name": "test",
        "last_name": "invalidemail",
        "avatar": "https://example.com/avatar.jpg"
    }
    response = user_client.create_user_raw(user=payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"ERROR {response.status_code} {response.text}"
    body = response.json()

@pytest.mark.parametrize("avatar_url", [
    "",
    None,
    "https://",
    "not-a-url",
    "www.example.com/avatar.jpg",
])
def test_create_user_invalid_avatar_url(user_client: UserApiClient, avatar_url: Any):
    payload = {
        "email": "test@example.com",
        "first_name": "test",
        "last_name": "invalidavatar",
        "avatar": avatar_url
    }
    response = user_client.create_user_raw(user=payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"ERROR {response.status_code} {response.text}"
    body = response.json()

@pytest.mark.parametrize("missing_field, payload", [
    ("email", {
        "first_name": "Test",
        "last_name": "MissingEmail",
        "avatar": "https://example.com/avatar.jpg"
    }),
    ("first_name", {
        "email": "test@example.com",
        "last_name": "MissingFirst",
        "avatar": "https://example.com/avatar.jpg"
    }),
    ("last_name", {
        "email": "test@example.com",
        "first_name": "MissingLast",
        "avatar": "https://example.com/avatar.jpg"
    }),
    ("avatar", {
        "email": "test@example.com",
        "first_name": "MissingAvatar",
        "last_name": "Last"
    }),
])
def test_create_user_missing_required_fields(user_client: UserApiClient, missing_field: str, payload: dict):
    response = user_client.create_user_raw(user=payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"ERROR {response.status_code} {response.text}"

@pytest.mark.parametrize("detail, method", [("Method Not Allowed", "PATCH")])
def test_create_user_invalid_method(user_client: UserApiClient, detail: str, method: str):
    payload = {
        "email": "test@example.com",
        "first_name": "test",
        "last_name": "invalidmethod",
        "avatar": "https://example.com/avatar.jpg"
    }
    response = user_client.create_user_raw(user=payload, method=method)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, f"ERROR {response.status_code} {response.text}"
    body = response.json()
    assert body["detail"] == detail, f"Expected detail {detail}, but got {body['detail']}"