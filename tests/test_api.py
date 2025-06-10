import math
import json
from http import HTTPStatus

import pytest
import requests
from jsonschema import validate
from models.User import User
from schemas.single_user_schema import single_user

@pytest.fixture()
def all_users(app_url):
    response = requests.get(f"{app_url}/api/users/all")
    assert response.status_code == HTTPStatus.OK
    return response.json()

@pytest.fixture()
def all_users_count(all_users):
    return len(all_users)

# test for DB data integrity
def test_user_no_duplicates(all_users):
    user_ids = [user["id"] for user in all_users]
    assert len(user_ids) == len(set(user_ids))

# tests for pagination in GET users
@pytest.mark.parametrize("page, size", [(1, 30), (4, 3), (3, 20), (1, 100)])
def test_users_items_count_respects_page_and_size(app_url, all_users_count, page, size):
    response = requests.get(f"{app_url}/api/users", params={"page":page, "size":size})
    assert response.status_code == 200

    body = response.json()
    expected_pages = math.ceil(all_users_count / size)

    assert len(body["items"]) <= size, f"Expected size {size}, but got {body['size']}"
    if page < expected_pages:
        assert len(body["items"]) == size, f"Expected on not last page user count {size}, but got {len(body['items'])}"
    elif page == expected_pages:
        expected_last_page_count = all_users_count % size or size
        assert len(body["items"]) == expected_last_page_count, f"Expected on last page user count {expected_last_page_count}, but got {len(body['items'])}"

@pytest.mark.parametrize("page, size", [(1, 10),(1, 25), (2, 20), (3, 5), (1, 100)])
def test_users_pagination_metadata(app_url, all_users_count, page, size):
    response = requests.get(f"{app_url}/api/users", params={"page":page, "size":size})
    assert response.status_code == 200

    body = response.json()
    expected_pages = math.ceil(all_users_count / size)

    assert body["page"] == page, f"Expected page {page}, but got {body['page']}"
    assert body["size"] == size, f"Expected size {size}, but got {body['size']}"
    assert body["total"] == all_users_count, f"Expected total {all_users_count}, but got {body['total']}"
    assert body["pages"] == expected_pages, f"Expected pages {expected_pages}, but got {body['pages']}"

@pytest.mark.parametrize("first_page, second_page, size", [(1, 2, 25), (3, 4, 10)])
def test_users_return_different_data_on_different_pages(app_url, first_page, second_page, size):
    r1 = requests.get(f"{app_url}/api/users", params={"page": first_page, "size": size}).json()
    r2 = requests.get(f"{app_url}/api/users", params={"page": second_page, "size": size}).json()

    ids_page_1 = [user["id"] for user in r1["items"]]
    ids_page_2 = [user["id"] for user in r2["items"]]

    assert set(ids_page_1) != set(ids_page_2), "Expected different sets of user IDs on different pages"

@pytest.mark.parametrize("page, size", [(1, 30), (4, 3), (3, 20)])
def test_users_user_model_validation_by_pagination(app_url, page, size):
    response = requests.get(f"{app_url}/api/users", params={"page":page, "size":size})
    assert response.status_code == 200

    body = response.json()
    users = body["items"]

    assert users, f"No users returned for page {page} and size {size}"
    assert isinstance(users, list)
    for user in users:
        User.model_validate(user)

@pytest.mark.parametrize("default_page, default_size", [(1, 50)])
def test_users_default_pagination(app_url, all_users_count, default_page, default_size):
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == 200

    body = response.json()
    page = body["page"]
    expected_pages = math.ceil(all_users_count / default_size)

    assert body["page"] == default_page, f"Expected default_page {default_page}, but got {body['page']}"
    assert body["size"] == default_size, f"Expected default_size {default_size}, but got {body['size']}"
    assert body["total"] == all_users_count, f"Expected total users {all_users_count}, but got {body['total']}"
    assert body["pages"] == expected_pages, f"Expected pages {expected_pages}, but got {body['pages']}"
    assert len(body["items"]) <= default_size, f"Expected user count {default_size}, but got {len(body['items'])}"
    if page < expected_pages:
        assert len(body["items"]) == default_size, f"Expected on not last page user count {default_size}, but got {len(body['items'])}"
    elif page == expected_pages:
        expected_last_page_count = all_users_count % default_size or default_size
        assert len(body["items"]) == expected_last_page_count, f"Expected on last page user count {expected_last_page_count}, but got {len(body['items'])}"

@pytest.mark.parametrize("page", [999, 2500])
def test_users_empty_data_on_page(app_url, page):
    response = requests.get(f"{app_url}/api/users", params={"page":page})
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert len(body["items"]) == 0, f"Expected no items, but got {len(body['items'])}"

@pytest.mark.parametrize("page", [-1, 0, "abc"])
def test_users_invalid_page(app_url, page):
    response = requests.get(f"{app_url}/api/users", params={"page":page})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status code 422, but got {response.status_code}"

@pytest.mark.parametrize("page, size", [(200, 100), (1500, 20)])
def test_users_size_greater_than_total_count(app_url, page, size):
    response = requests.get(f"{app_url}/api/users", params={"page":page, "size":size})
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    users = body["items"]
    assert len(users) == 0, f"Expected no items, but got {len(users)}"

@pytest.mark.parametrize("size", [-1, 0, 101, 1000, "abc"])
def test_users_page_with_invalid_size(app_url, size):
    response = requests.get(f"{app_url}/api/users", params={"size":size})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status code 422, but got {response.status_code}"

# tests for GET user
@pytest.mark.parametrize("user_id", [1, 12, 53])
def test_user(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.OK, f"Expected status code 200, but got {response.status_code}"

    user = response.json()
    User.model_validate(user)

@pytest.mark.parametrize("user_id", [1000])
def test_user_nonexistent_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.parametrize("user_id", [-1, 0, "hello"])
def test_user_invalid_value(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

@pytest.mark.parametrize("user_id", [2])
def test_single_user_schema_validate_from_file(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.OK

    body = response.json()

    validate(body, schema=single_user)

@pytest.mark.parametrize(
    "user_id, first_name, last_name, email, avatar",
    [(2, "George", "Bluth", "george.bluth@reqres.in", "https://reqres.in/img/faces/1-image.jpg")]
)
def test_user_data(app_url, user_id, first_name, last_name, email, avatar):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == 200

    body = response.json()

    assert body["id"] == user_id, f"Expected first_name {user_id}, but got {body['id']}"
    assert body["first_name"] == first_name, f"Expected first_name {first_name}, but got {body['first_name']}"
    assert body["last_name"] == last_name, f"Expected last_name {last_name}, but got {body['last_name']}"
    assert body["email"] == email, f"Expected email {email}, but got {body['email']}"
    assert body["avatar"] == avatar, f"Expected avatar {avatar}, but got {body['avatar']}"

@pytest.mark.parametrize("user_id, message", [(1000, "User not found")])
def test_user_not_found(app_url, user_id, message):
    response = requests.get(f"{app_url}/api/users/{user_id}")

    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"

    body = response.json()

    assert "message" in body, "Response body does not contain 'message' key"
    assert body["message"] == message, f"Expected avatar {message}, but got {body['message']}"

# tests for POST user create
@pytest.mark.parametrize(
    "email, first_name, last_name, avatar",
    [("janet.weaver@reqres.in", "Janet", "Weaver", "https://reqres.in/img/faces/54-image.jpg")]
)
def test_create_user(app_url, email, first_name, last_name, avatar):
    response = requests.post(
        f"{app_url}/api/users",
        json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar}
    )

    assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    body = response.json()

    assert body["id"] is not None, f"Expected id {body['id']}, but got {body['id']}"
    assert body["email"] == email, f"Expected email {email}, but got {body['email']}"
    assert body["first_name"] == first_name, f"Expected first_name {first_name}, but got {body['first_name']}"
    assert body["last_name"] == last_name, f"Expected last_name {last_name}, but got {body['last_name']}"
    assert body["avatar"] == avatar, f"Expected avatar {avatar}, but got {body['avatar']}"

# add late after DB
# @pytest.mark.parametrize(
#     "email, first_name, last_name, avatar, message",
#     [("janet.weaver@reqres.in", "Janet", "Weaver", "https://reqres.in/img/faces/3-image.jpg", "Email already registered")]
# )
# def test_create_existing_email(app_url, email, first_name, last_name, avatar, message):
#     response = requests.post(
#     f"{app_url}/api/users",
#         json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar}
#     )
#     assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
#     body = response.json()
#     assert "message" in body, "Response body does not contain 'message' key"
#     assert body["message"] == message, f"Expected message {message}, but got {body['message']}"

# tests for PUT user update
@pytest.mark.parametrize(
    "user_id, email, first_name, last_name, avatar",
    [(2, "janet.weaver@reqres.in", "Janet", "Ferguson", "https://reqres.in/img/faces/222-image.jpg")]
)
def test_update_user(app_url, user_id, email, first_name, last_name, avatar):
    response = requests.put(
        f"{app_url}/api/users/{user_id}",
        json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar}
    )

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    body = response.json()

    assert body["email"] == email, f"Expected email {email}, but got {body['email']}"
    assert body["first_name"] == first_name, f"Expected first_name {first_name}, but got {body['first_name']}"
    assert body["last_name"] == last_name, f"Expected last_name {last_name}, but got {body['last_name']}"
    assert body["avatar"] == avatar, f"Expected avatar {avatar}, but got {body['avatar']}"

@pytest.mark.parametrize(
    "user_id, email, first_name, last_name, avatar, message",
    [(2500, "janet.weaver@reqres.in", "Janet", "Ferguson", "https://reqres.in/img/faces/3-image.jpg", "User not found")]
)
def test_update_not_existing_user(app_url, user_id, email, first_name, last_name, avatar, message):
    response = requests.put(
        f"{app_url}/api/users/{user_id}",
        json={"email": email, "first_name": first_name, "last_name": last_name, "avatar": avatar}
    )

    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"

    body = response.json()

    assert "message" in body, "Response body does not contain 'message' key"
    assert body["message"] == message, f"Expected message {message}, but got {body['message']}"

# tests for DELETE user delete

@pytest.mark.parametrize("user_id", [2])
def test_delete_user(app_url, user_id):
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    assert response.status_code == 204, f"Expected status code 204, but got {response.status_code}"

@pytest.mark.parametrize("user_id, message", [(304, "User not found")])
def test_delete_not_existing_user(app_url, user_id, message):
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    body = response.json()

    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
    assert body["message"] == message, f"Expected message {message}, but got {body['message']}"