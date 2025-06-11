import os
import dotenv
import json
import pytest
import requests
from http import HTTPStatus
from faker import Faker

fake = Faker()

@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()

@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")

@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open("../users.json") as f:
        test_data_user = json.load(f)
    api_users = []
    for user in test_data_user:
        response = requests.post(f"{app_url}/api/users", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")

@pytest.fixture
def user_payload_factory():
    def _factory():
        return {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }
    return _factory

@pytest.fixture
def created_user(app_url, user_payload_factory):
    user = user_payload_factory()
    response = requests.post(f"{app_url}/api/users", json=user)
    assert response.status_code == HTTPStatus.CREATED
    return response.json()

@pytest.fixture
def created_user_cleanup(app_url):
    created_user_ids = []

    yield created_user_ids

    for user_id in created_user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")


@pytest.fixture
def all_users(app_url):
    response = requests.get(f"{app_url}/api/users/all")
    assert response.status_code == HTTPStatus.OK
    return response.json()

@pytest.fixture
def all_users_count(all_users):
    return len(all_users)
