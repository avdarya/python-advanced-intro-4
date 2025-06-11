from http import HTTPStatus

import pytest
import requests

def test_update_user(app_url, user_payload_factory, created_user, created_user_cleanup):
    user_id = created_user["id"]
    user_for_update = user_payload_factory()
    response = requests.patch(f"{app_url}/api/users/{user_id}", json=user_for_update)
    assert response.status_code == HTTPStatus.OK, f"Expected status code 200, but got {response.status_code}"
    body = response.json()
    created_user_cleanup.append(user_id)
    assert "id" in body and isinstance(body["id"], int), f"Expected id: int = {body['id']}, but got {body['id']}"
    assert body["id"] == user_id, f"Expected id: {user_id}, but got {body['id']}"
    assert body["email"] == user_for_update['email'], f"Expected email {user_for_update['email']}, but got {body['email']}"
    assert body["first_name"] == user_for_update['first_name'], f"Expected first_name {user_for_update['first_name']}, but got {body['first_name']}"
    assert body["last_name"] == user_for_update['last_name'], f"Expected last_name {user_for_update['last_name']}, but got {body['last_name']}"
    assert body["avatar"] == user_for_update['avatar'], f"Expected avatar {user_for_update['avatar']}, but got {body['avatar']}"


@pytest.mark.parametrize("field", ["email", "first_name", "last_name", "avatar"])
def test_update_user_by_one_field(app_url, created_user, user_payload_factory, created_user_cleanup, field):
    user_id = created_user["id"]
    updated_field = user_payload_factory()[field]
    payload = {f"{field}": updated_field}
    response = requests.patch(f"{app_url}/api/users/{user_id}", json=payload)
    body = response.json()
    created_user_cleanup.append(user_id)
    assert response.status_code == HTTPStatus.OK, f"Expected status code 200, but got {response.status_code}"
    assert body["id"] == user_id, f"Expected id: {user_id}, but got {body['id']}"
    assert body[f"{field}"] == updated_field, f"Expected email {updated_field}, but got {body[f'{field}']}"

def test_update_then_get_user_returns_same_data(app_url, user_payload_factory, created_user, created_user_cleanup):
    user_id = created_user["id"]
    user_for_update = user_payload_factory()
    response = requests.patch(f"{app_url}/api/users/{user_id}", json=user_for_update)
    assert response.status_code == HTTPStatus.OK
    api_response = requests.get(f"{app_url}/api/users/{user_id}")
    api_user = api_response.json()
    created_user_cleanup.append(user_id)
    assert api_response.status_code == HTTPStatus.OK
    assert api_user["id"] == user_id, f"Expected id: {user_id}, but got {api_user['id']}"
    assert api_user["email"] == user_for_update["email"], f"Expected email {user_for_update['email']}, but got {api_user['email']}"
    assert api_user["first_name"] == user_for_update["first_name"], f"Expected first_name {user_for_update['first_name']}, but got {api_user['first_name']}"
    assert api_user["last_name"] == user_for_update["last_name"], f"Expected last_name {user_for_update['last_name']}, but got {api_user['last_name']}"
    assert api_user["avatar"] == user_for_update["avatar"], f"Expected first_name {user_for_update['avatar']}, but got {api_user['avatar']}"

@pytest.mark.parametrize("err_msg", ["User not found"])
def test_update_not_existing_user(app_url, created_user, user_payload_factory, err_msg):
    user_id = created_user["id"]
    updated_user = user_payload_factory()
    requests.delete(f"{app_url}/api/users/{user_id}")
    response = requests.patch(f"{app_url}/api/users/{user_id}", json=updated_user)
    body = response.json()
    assert response.status_code == HTTPStatus.NOT_FOUND, f"Expected status code 404, but got {response.status_code}"
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
def test_update_user_invalid_email(app_url, created_user, created_user_cleanup, email, err_msg):
    user_id = created_user["id"]
    payload = {"email": email}
    response = (requests.patch(f"{app_url}/api/users/{user_id}", json=payload))
    created_user_cleanup.append(user_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected status code 400, but got {response.status_code}"
    body = response.json()
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"


@pytest.mark.parametrize("avatar_url, err_msg", [
    ("", "invalid data"),
    ("https://", "invalid data"),
    ("not-a-url", "invalid data"),
    ("www.example.com/avatar.jpg", "invalid data")
])
def test_update_user_invalid_avatar_url(app_url, created_user, created_user_cleanup, avatar_url, err_msg):
    user_id = created_user["id"]
    payload = {"avatar": avatar_url}
    response = (requests.patch(f"{app_url}/api/users/{user_id}", json=payload))
    created_user_cleanup.append(user_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Expected status code 400, but got {response.status_code}"
    body = response.json()
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("err_msg, invalid_id", [("Unprocessable Entity", 0), ("Unprocessable Entity", -1)])
def test_update_user_invalid_user_id(app_url, created_user, created_user_cleanup, err_msg, invalid_id):
    user_id = created_user["id"]
    payload = {"last_name": "invalidid"}
    response = requests.patch(f"{app_url}/api/users/{invalid_id}", json=payload)
    created_user_cleanup.append(user_id)
    body = response.json()
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status code 422, but got {response.status_code}"
    assert body["message"] == err_msg, f"Expected message {err_msg}, but got {body['message']}"

@pytest.mark.parametrize("detail", ["Method Not Allowed"])
def test_update_user_invalid_method(app_url, created_user, created_user_cleanup, detail):
    user_id = created_user["id"]
    payload = {"last_name": "invalidmethod"}
    response = requests.put(f"{app_url}/api/users/{user_id}", json=payload)
    body = response.json()
    created_user_cleanup.append(user_id)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, f"Expected status code 405, but got {response.status_code}"
    assert body["detail"] == detail, f"Expected detail {detail}, but got {body['detail']}"
