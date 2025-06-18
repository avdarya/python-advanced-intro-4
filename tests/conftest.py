import os
from typing import Generator, Callable

import dotenv
import json
import pytest
import requests
from http import HTTPStatus
from faker import Faker

from app.models.User import UserCreate
from clients.status_client import StatusApiClient
from clients.user_client import UserApiClient

fake = Faker()

@pytest.fixture(scope="session", autouse=True)
def envs() -> None:
    dotenv.load_dotenv()

@pytest.fixture(scope="session")
def app_url() -> str | None:
    return os.getenv("APP_URL")

def pytest_addoption(parser) -> None:
    parser.addoption("--env", default="dev")

@pytest.fixture(scope="session")
def env(request) -> str:
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def user_client(env: str) -> UserApiClient:
    return UserApiClient(env)

@pytest.fixture(scope="session")
def status_client(env: str) -> StatusApiClient:
    return StatusApiClient(env)

@pytest.fixture(scope="module")
def fill_test_data(user_client: UserApiClient) -> Generator[list[int], None, None]:
    file_path = os.path.join(os.path.dirname(__file__), '..', 'users.json')
    with open(file_path, 'r') as f:
        test_data_user = json.load(f)
    # with open("../users.json") as f:
    #     test_data_user = json.load(f)
    api_users = []
    for user in test_data_user:
        response = user_client.create_user_validated(user=UserCreate(**user))
        print('FROM FIX')
        print(response.text)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        user_client.delete_user(user_id)

@pytest.fixture
def user_payload_factory() -> Callable[[], dict]:
    def _factory():
        return {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }
    return _factory

@pytest.fixture
def created_user(user_client: UserApiClient, user_payload_factory: Callable[[], dict]) -> dict:
    user = user_payload_factory()
    response = user_client.create_user_validated(user=UserCreate(**user))
    assert response.status_code == HTTPStatus.CREATED
    return response.json()

@pytest.fixture
def created_user_cleanup(user_client: UserApiClient) -> Generator[list[int], None, None]:
    created_user_ids = []

    yield created_user_ids

    for user_id in created_user_ids:
        user_client.delete_user(user_id)

@pytest.fixture
def all_users(user_client: UserApiClient) -> list:
    response = user_client.get_all_users()
    assert response.status_code == HTTPStatus.OK
    return response.json()

@pytest.fixture
def all_users_count(all_users: list) -> int:
    return len(all_users)