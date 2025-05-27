import json
import pytest
import requests

from jsonschema import validate
from single_user_schema import single_user

url = "https://reqres.in/api/users"
headers = {'x-api-key': 'reqres-free-v1'}

@pytest.mark.parametrize("user_id", [2])
def test_schema_validate_from_file(user_id):
    response = requests.get(f"{url}/{user_id}", headers=headers)
    body = response.json()

    assert response.status_code == 200
    with open("single_user.json") as f:
        validate(body, schema=json.loads(f.read()))

@pytest.mark.parametrize("user_id", [2])
def test_schema_validate_from_variable(user_id):
    response = requests.get(f"{url}/{user_id}", headers=headers)
    body = response.json()

    assert response.status_code == 200
    validate(body, schema=single_user)

@pytest.mark.parametrize("user_id, first_name, last_name, email", [(2, "Janet", "Weaver", "janet.weaver@reqres.in")])
def test_fio_email_from_req_returns_in_resp(user_id, first_name, last_name, email):
    response = requests.get(f"{url}/{user_id}", headers=headers)
    body = response.json()
    data = body["data"]

    assert data["first_name"] == first_name
    assert data["last_name"] == last_name
    assert data["email"] == email

@pytest.mark.parametrize("page", [2])
def test_get_users_returns_unique_users(page):
    response = requests.get(url, headers=headers, params={"page": page})
    body = response.json()

    ids = [element["id"] for element in body["data"]]

    assert len(ids) == len(set(ids))