import http

import pytest
from faker import Faker

from tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio

fake = Faker()

url_template = "{service_url}/api/v1/auth/signup"
url = url_template.format(service_url=test_settings.app_dsn)
headers = {"Content-Type": "application/json"}


async def test_registration(session, db_truncate):

    user = {
        "email": fake.email(),
        "password": fake.password(),
        "full_name": fake.name(),
        "username": fake.simple_profile()["username"],
    }

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

    async with session.post(url, json=user) as response:

        await response.json()
        assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY
