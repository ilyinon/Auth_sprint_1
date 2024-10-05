import http

import pytest
from faker import Faker

from tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio

fake = Faker()

url_template = "{service_url}/api/v1/auth/{endpoint}"

headers = {"Content-Type": "application/json"}

user = {
    "email": fake.email(),
    "password": fake.password(),
    "full_name": fake.name(),
    "username": fake.simple_profile()["username"],
}


async def test_registration(session, db_truncate):
    endpoint = "signup"
    url = url_template.format(service_url=test_settings.app_dsn, endpoint=endpoint)
    async with session.post(url, json=user) as response:

        body = await response.json()
        assert response.status == http.HTTPStatus.OK
        assert body["email"] == user["email"]
        assert body["full_name"] == user["full_name"]
        assert body["email"] == user["email"]
        assert body["username"] == user["username"]


@pytest.mark.parametrize(
    "user",
    [
        (
            {
                "email": "bad_email",
                "username": fake.simple_profile()["username"],
                "full_name": fake.name(),
                "password": fake.password(),
            }
        ),
        (
            {
                "email": fake.email(),
                "username": fake.simple_profile()["username"],
                "full_name": fake.name(),
            }
        ),
        (
            {
                "email": fake.email(),
                "username": fake.simple_profile()["username"],
                "password": fake.password(),
            }
        ),
        (
            {
                "username": fake.simple_profile()["username"],
                "full_name": fake.name(),
                "password": fake.password(),
            }
        ),
    ],
)
async def test_register_validation(session, user, db_truncate):
    endpoint = "signup"
    url = url_template.format(service_url=test_settings.app_dsn, endpoint=endpoint)

    async with session.post(url, json=user) as response:

        await response.json()
        assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY


async def test_check_access_no_token(session):
    endpoint = "check_access"
    url = url_template.format(service_url=test_settings.app_dsn, endpoint=endpoint)

    async with session.get(url) as response:
        await response.json()

    assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY


async def test_login(session):
    endpoint = "login"
    url = url_template.format(service_url=test_settings.app_dsn, endpoint=endpoint)
    login_data = {"email": user["email"], "password": user["password"]}

    async with session.post(url, json=login_data) as response:

        body = await response.json()

        assert response.status == http.HTTPStatus.OK
        assert isinstance(body["access_token"], str)
        assert isinstance(body["refresh_token"], str)


async def test_check_access(session):
    endpoint_login = "login"
    endpoint_check_access = "check_access"
    url_login = url_template.format(
        service_url=test_settings.app_dsn, endpoint=endpoint_login
    )
    url_check_access = url_template.format(
        service_url=test_settings.app_dsn, endpoint=endpoint_check_access
    )

    login_data = {"email": user["email"], "password": user["password"]}

    async with session.post(url_login, json=login_data) as response:

        body = await response.json()
        access_token = body["access_token"]

    async with session.get(
        url_check_access, headers={"Authorization": f"Bearer {access_token}"}
    ):
        assert response.status == http.HTTPStatus.OK


async def test_refresh_token(session):
    endpoint_login = "login"
    endpoint_refresh_token = "refresh"
    endpoint_check_access = "check_access"

    url_login = url_template.format(
        service_url=test_settings.app_dsn, endpoint=endpoint_login
    )
    url_refresh_token = url_template.format(
        service_url=test_settings.app_dsn, endpoint=endpoint_refresh_token
    )
    url_check_access = url_template.format(
        service_url=test_settings.app_dsn, endpoint=endpoint_check_access
    )

    login_data = {"email": user["email"], "password": user["password"]}

    async with session.post(url_login, json=login_data) as response:

        body = await response.json()
        refresh_token = body["refresh_token"]
        access_token = body["access_token"]

    """
    Refersh token and get new access_token
    """
    async with session.post(
        url_refresh_token, json={"refresh_token": refresh_token}
    ) as response:
        body = await response.json()
        new_access_token = body["access_token"]
        assert response.status == http.HTTPStatus.OK

    """
    Verify if new access token works
    """
    async with session.get(
        url_check_access, headers={"Authorization": f"Bearer {new_access_token}"}
    ) as response:
        assert response.status == http.HTTPStatus.OK

    """
    Verify if old access token doesn't work
    """
    # TODO: enable as JTI will be stored black list redis
    # async with session.get(
    #     url_check_access, headers={"Authorization": f"Bearer {access_token}"}
    # ) as response:
    #     assert response.status == http.HTTPStatus.UNAUTHORIZED