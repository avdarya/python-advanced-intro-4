import json
import pytest
import requests

from jsonschema import validate
from single_user_schema import single_user

url = "http://0.0.0.0:8000/api/users"

@pytest.mark.parametrize("user_id", [2])
def test_schema_validate_from_file(user_id):
    response = requests.get(f"{url}/{user_id}")
    body = response.json()

    assert response.status_code == 200
    with open("single_user.json") as f:
        validate(body, schema=json.loads(f.read()))

@pytest.mark.parametrize("user_id", [2])
def test_schema_validate_from_variable(user_id):
    response = requests.get(f"{url}/{user_id}")
    body = response.json()

    assert response.status_code == 200
    validate(body, schema=single_user)

@pytest.mark.parametrize(
    "user_id, first_name, last_name, email, avatar",
    [(2, "Naomi", "Wall", "libero@hotmail.edu", "https://reqres.in/img/faces/2-image.jpg")]
)
def test_user_data(user_id, first_name, last_name, email, avatar):
    response = requests.get(f"{url}/{user_id}")

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    body = response.json()

    assert "data" in body,  "Response body does not contain 'data' key"

    data = body["data"]

    assert data["first_name"] == first_name, f"Expected first_name {first_name}, but got {data['first_name']}"
    assert data["last_name"] == last_name, f"Expected last_name {last_name}, but got {data['last_name']}"
    assert data["email"] == email, f"Expected email {email}, but got {data['email']}"
    assert data["avatar"] == avatar, f"Expected avatar {avatar}, but got {data['avatar']}"

@pytest.mark.parametrize("user_id, message", [(1, "User not found")])
def test_user_not_found(user_id, message):
    response = requests.get(f"{url}/{user_id}")

    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"

    body = response.json()

    assert "message" in body, "Response body does not contain 'message' key"

    assert body["message"] == message, f"Expected avatar {message}, but got {body['message']}"

@pytest.mark.parametrize(
    "email, first_name, last_name, avatar",
    [("janet.weaver@reqres.in", "Janet", "Weaver", "https://reqres.in/img/faces/3-image.jpg")]
)
def test_create_user(email, first_name, last_name, avatar):
    response = requests.post(url, json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar})

    body = response.json()

    assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"
    assert body["email"] == email, f"Expected email {email}, but got {body['email']}"
    assert body["first_name"] == first_name, f"Expected first_name {first_name}, but got {body['first_name']}"
    assert body["last_name"] == last_name, f"Expected last_name {last_name}, but got {body['last_name']}"
    assert body["avatar"] == avatar, f"Expected avatar {avatar}, but got {body['avatar']}"
    assert body["id"] is not None, f"Expected id {body['id']}, but got {body['id']}"
    assert body["created_at"] is not None, f"Expected created_at {body['created_at']}, but got {body['created_at']}"
    assert body["updated_at"] is not None, f"Expected updated_at {body['updated_at']}, but got {body['updated_at']}"

@pytest.mark.parametrize(
    "email, first_name, last_name, avatar, message",
    [("janet.weaver@reqres.in", "Janet", "Weaver", "https://reqres.in/img/faces/3-image.jpg", "Email already registered")]
)
def test_create_existing_email(email, first_name, last_name, avatar, message):
    response = requests.post(url, json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar})

    body = response.json()

    assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
    assert "message" in body, "Response body does not contain 'message' key"
    assert body["message"] == message, f"Expected message {message}, but got {body['message']}"

@pytest.mark.parametrize(
    "user_id, email, first_name, last_name, avatar",
    [(2, "janet.weaver@reqres.in", "Janet", "Ferguson", "https://reqres.in/img/faces/3-image.jpg")]
)
def test_update_user(user_id, email, first_name, last_name, avatar):
    response = requests.put(url=f"{url}/{user_id}", json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar})
    body = response.json()

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert body["email"] == email, f"Expected email {email}, but got {body['email']}"
    assert body["first_name"] == first_name, f"Expected first_name {first_name}, but got {body['first_name']}"
    assert body["last_name"] == last_name, f"Expected last_name {last_name}, but got {body['last_name']}"
    assert body["avatar"] == avatar, f"Expected avatar {avatar}, but got {body['avatar']}"
    assert body["updated_at"] is not None, f"Expected updated_at {body['updated_at']}, but got {body['updated_at']}"

@pytest.mark.parametrize(
    "user_id, email, first_name, last_name, avatar, message",
    [(1, "janet.weaver@reqres.in", "Janet", "Ferguson", "https://reqres.in/img/faces/3-image.jpg", "User not found")]
)
def test_update_not_existing_user(user_id, email, first_name, last_name, avatar, message):
    response = requests.put(url=f"{url}/{user_id}", json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar})
    body = response.json()

    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
    assert "message" in body, "Response body does not contain 'message' key"
    assert body["message"] == message, f"Expected message {message}, but got {body['message']}"

@pytest.mark.parametrize("user_id", [2])
def test_delete_user(user_id):
    response = requests.delete(f"{url}/{user_id}")

    assert response.status_code == 204, f"Expected status code 204, but got {response.status_code}"

@pytest.mark.parametrize("user_id, message", [(1, "User not found")])
def test_delete_not_existing_user(user_id, message):
    response = requests.delete(f"{url}/{user_id}")
    body = response.json()

    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
    assert body["message"] == message, f"Expected message {message}, but got {body['message']}"