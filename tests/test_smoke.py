import requests
from http import HTTPStatus

from models.AppStatus import AppStatus

def test_status_available(app_url):
    response = requests.get(f"{app_url}/status")
    assert response.status_code == HTTPStatus.OK, f"Expected status code 200, but got {response.status_code}"

def test_status_response_structure(app_url):
    response = requests.get(f"{app_url}/status")

    status_data = AppStatus(**response.json())
    assert isinstance(status_data, AppStatus), "Response model does not match expected type AppStatus"

def test_status_has_users_field(app_url):
    response = requests.get(f"{app_url}/status")

    data = response.json()
    assert "users" in data, "'users' not found in response"
    assert isinstance(data["users"], bool), "'users' is not a boolean"

def test_status_users_true(app_url):
    response = requests.get(f"{app_url}/status")

    data = response.json()
    assert data["users"] is True, "'users' is not True"

def test_status_response_headers(app_url):
    response = requests.get(f"{app_url}/status")

    assert response.headers["Content-Type"] == "application/json", f"Expected Content-Type = application/json, but got {response.headers['Content-Type']}"

def test_status_response_time(app_url):
    response = requests.get(f"{app_url}/status")

    assert response.elapsed.total_seconds() < 1.0