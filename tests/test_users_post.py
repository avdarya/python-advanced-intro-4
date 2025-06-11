from http import HTTPStatus

import pytest
import requests

def test_create_user(app_url, user_payload_factory, created_user_cleanup):
    user = user_payload_factory()
    response = (requests.post(f"{app_url}/api/users", json=user))
    body = response.json()
    created_user_cleanup.append(body["id"])
    assert response.status_code == HTTPStatus.CREATED, f"Expected status code 201, but got {response.status_code}"
    assert "id" in body and isinstance(body["id"], int), f"Expected id: int = {body['id']}, but got {body['id']}"
    assert body["email"] == user["email"], f"Expected email {user['email']}, but got {body['email']}"
    assert body["first_name"] == user["first_name"], f"Expected first_name {user['first_name']}, but got {body['first_name']}"
    assert body["last_name"] == user["last_name"], f"Expected last_name {user['last_name']}, but got {body['last_name']}"
    assert body["avatar"] == user["avatar"], f"Expected avatar {user['avatar']}, but got {body['avatar']}"

def test_create_then_get_user_returns_same_data(app_url, user_payload_factory, created_user_cleanup):
    user = user_payload_factory()
    response = requests.post(f"{app_url}/api/users", json=user)
    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    api_response = requests.get(f"{app_url}/api/users/{body['id']}")
    api_user = api_response.json()
    created_user_cleanup.append(body["id"])
    assert api_response.status_code == HTTPStatus.OK
    assert api_user["id"] == body["id"]
    assert api_user["email"] == user["email"]
    assert api_user["first_name"] == user["first_name"]
    assert api_user["last_name"] == user["last_name"]
    assert api_user["avatar"] == user["avatar"]

@pytest.mark.parametrize("email, err_msg", [
    ("", "invalid data"),
    (None, "invalid data"),
    ("libereddfo@@hotmail.edu", "invalid data"),
    ("janet.weaverreqres.in", "invalid data"),
    ("@reqres.in", "invalid data"),
    ("michael.lawson@reqres", "invalid data"),
    ("tracey.ramos@", "invalid data")
])
def test_create_user_invalid_email(app_url, email, err_msg):
    payload = {
        "email": email,
        "first_name": "test",
        "last_name": "invalidemail",
        "avatar": "https://example.com/avatar.jpg"
    }
    response = (requests.post(f"{app_url}/api/users", json=payload))
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected status code 400, but got {response.status_code}"
    body = response.json()
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("avatar_url, err_msg", [
    ("", "invalid data"),
    (None, "invalid data"),
    ("https://", "invalid data"),
    ("not-a-url", "invalid data"),
    ("www.example.com/avatar.jpg", "invalid data")
])
def test_create_user_invalid_avatar_url(app_url, avatar_url, err_msg):
    payload = {
        "email": "test@example.com",
        "first_name": "test",
        "last_name": "invalidavatar",
        "avatar": avatar_url
    }
    response = (requests.post(f"{app_url}/api/users", json=payload))
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected status code 400, but got {response.status_code}"
    body = response.json()
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("err_msg, missing_field, payload", [
    ("invalid data", "email", {
        "first_name": "Test",
        "last_name": "MissingEmail",
        "avatar": "https://example.com/avatar.jpg"
    }),
    ("invalid data", "first_name", {
        "email": "test@example.com",
        "last_name": "MissingFirst",
        "avatar": "https://example.com/avatar.jpg"
    }),
    ("invalid data", "last_name", {
        "email": "test@example.com",
        "first_name": "MissingLast",
        "avatar": "https://example.com/avatar.jpg"
    }),
    ("invalid data", "avatar", {
        "email": "test@example.com",
        "first_name": "MissingAvatar",
        "last_name": "Last"
    }),
])
def test_create_user_missing_required_fields(app_url, err_msg, missing_field, payload):
    response = requests.post(f"{app_url}/api/users", json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected status code 400, but got {response.status_code}"
    body = response.json()
    assert body["message"] == "invalid data", f"Missing field {missing_field} should trigger error"

@pytest.mark.parametrize("detail", ["Method Not Allowed"])
def test_create_user_invalid_method(app_url, detail):
    payload = {
        "email": "test@example.com",
        "first_name": "test",
        "last_name": "invalidmethod",
        "avatar": "https://example.com/avatar.jpg"
    }
    response = requests.patch(f"{app_url}/api/users", json=payload)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, f"Expected status code 405, but got {response.status_code}"
    body = response.json()
    assert body["detail"] == detail, f"Expected detail {detail}, but got {body['detail']}"
