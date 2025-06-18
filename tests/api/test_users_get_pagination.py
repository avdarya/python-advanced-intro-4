import math
import pytest
from http import HTTPStatus

from app.models.User import User
from clients.user_client import UserApiClient

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("page, size", [(1, 30), (2, 30), (4, 5)])
def test_users_items_count_respects_page_and_size(user_client: UserApiClient, all_users_count: int, page: int, size: int):
    last_page = math.ceil(all_users_count / size)
    if page >= last_page:
        pytest.skip(f"Skipping test because page {page} is the last page or beyond. Total pages: {last_page}")

    response = user_client.get_users(page=page, size=size)
    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == size, f"Expected on not last page user count {size}, but got {len(body['items'])}"


@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("size", [30, 20, 100])
def test_users_items_count_on_last_page(user_client: UserApiClient, all_users_count: int, size: int):
    last_page = math.ceil(all_users_count / size)
    expected_last_page_count = all_users_count % size or size
    response = user_client.get_users(page=last_page, size=size)
    body = response.json()

    assert response.status_code == 200
    assert len(body["items"]) == expected_last_page_count, f"Expected on last page user count {expected_last_page_count}, but got {len(body['items'])}"

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("page, size", [(1, 10),(1, 25), (2, 20), (3, 5), (1, 100)])
def test_users_pagination_metadata(user_client: UserApiClient, all_users_count: int, page: int, size: int):
    response = user_client.get_users(page=page, size=size)

    assert response.status_code == 200

    body = response.json()
    expected_pages = math.ceil(all_users_count / size)

    assert body["page"] == page, f"Expected page {page}, but got {body['page']}"
    assert body["size"] == size, f"Expected size {size}, but got {body['size']}"
    assert body["total"] == all_users_count, f"Expected total {all_users_count}, but got {body['total']}"
    assert body["pages"] == expected_pages, f"Expected pages {expected_pages}, but got {body['pages']}"

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("first_page, second_page, size", [(1, 2, 25), (3, 4, 10)])
def test_users_return_different_data_on_different_pages(user_client: UserApiClient, first_page: int, second_page: int, size: int):
    r1 = user_client.get_users(page=first_page, size=size).json()
    r2 = user_client.get_users(page=second_page, size=size).json()

    ids_page_1 = [user["id"] for user in r1["items"]]
    ids_page_2 = [user["id"] for user in r2["items"]]

    assert set(ids_page_1) != set(ids_page_2), "Expected different sets of user IDs on different pages"

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("page, size", [(1, 30), (4, 3), (3, 20)])
def test_users_user_model_validation_by_pagination(user_client: UserApiClient, page: int, size:int):
    response = user_client.get_users(page=page, size=size)
    assert response.status_code == 200

    body = response.json()
    users = body["items"]

    assert users, f"No users returned for page {page} and size {size}"
    assert isinstance(users, list)
    for user in users:
        User.model_validate(user)

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("default_page, default_size", [(1, 50)])
def test_users_default_pagination(user_client: UserApiClient, all_users_count: int, default_page: int, default_size: int):
    response = user_client.get_users()
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

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("page", [999, 2500])
def test_users_empty_data_on_page(user_client: UserApiClient, page: int):
    response = user_client.get_users(page=page)
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert len(body["items"]) == 0, f"Expected no items, but got {len(body['items'])}"

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("page", [-1, 0, "abc"])
def test_users_invalid_page(user_client: UserApiClient, page: int | str):
    response = user_client.get_users(page=page)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status code 422, but got {response.status_code}"

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("page, size", [(200, 100), (1500, 20)])
def test_users_size_greater_than_total_count(user_client: UserApiClient, page: int, size: int):
    response = user_client.get_users(page=page, size=size)
    assert response.status_code == HTTPStatus.OK

    body = response.json()
    users = body["items"]
    assert len(users) == 0, f"Expected no items, but got {len(users)}"

@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("size", [-1, 0, 101, 1000])
def test_users_page_with_invalid_size(user_client: UserApiClient, size: int | str):
    response = user_client.get_users(size=size)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status code 422, but got {response.status_code}"