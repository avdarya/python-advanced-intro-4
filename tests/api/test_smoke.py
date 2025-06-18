from http import HTTPStatus

from app.models.AppStatus import AppStatus
from clients.status_client import StatusApiClient

def test_status_database_available(status_client: StatusApiClient):
    response = status_client.get_status()
    assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
    data = response.json()
    assert "database" in data, "'database' not found in response"
    assert isinstance(data["database"], bool), "'database' is not a boolean"
    assert data["database"] is True, "'database' is not True"

def test_status_response_structure(status_client: StatusApiClient):
    response = status_client.get_status()
    assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
    status_data = AppStatus(**response.json())
    assert isinstance(status_data, AppStatus), "Response model does not match expected type AppStatus"

def test_status_response_headers(status_client: StatusApiClient):
    response = status_client.get_status()
    assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
    assert response.headers["Content-Type"] == "application/json", f"Expected Content-Type = application/json, but got {response.headers['Content-Type']}"

def test_status_response_time(status_client: StatusApiClient):
    response = status_client.get_status()
    assert response.status_code == HTTPStatus.OK, f"ERROR {response.status_code} {response.text}"
    assert response.elapsed.total_seconds() < 1.0