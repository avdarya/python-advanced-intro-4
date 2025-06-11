import requests
from http import HTTPStatus

from app.models.AppStatus import AppStatus

def test_status_available(app_url):
    response = requests.get(f"{app_url}/status")
    assert response.status_code == HTTPStatus.OK, f"Expected status code 200, but got {response.status_code}"

def test_status_response_structure(app_url):
    response = requests.get(f"{app_url}/status")
    status_data = AppStatus(**response.json())
    assert isinstance(status_data, AppStatus), "Response model does not match expected type AppStatus"

def test_status_has_database_field(app_url):
    response = requests.get(f"{app_url}/status")

    data = response.json()
    assert "database" in data, "'database' not found in response"
    assert isinstance(data["database"], bool), "'database' is not a boolean"

def test_status_database_true(app_url):
    response = requests.get(f"{app_url}/status")
    data = response.json()
    assert data["database"] is True, "'database' is not True"

def test_status_response_headers(app_url):
    response = requests.get(f"{app_url}/status")
    assert response.headers["Content-Type"] == "application/json", f"Expected Content-Type = application/json, but got {response.headers['Content-Type']}"

def test_status_response_time(app_url):
    response = requests.get(f"{app_url}/status")
    assert response.elapsed.total_seconds() < 1.0