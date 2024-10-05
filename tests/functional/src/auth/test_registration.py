import http

import pytest
from faker import Faker

fake = Faker()


pytestmark = pytest.mark.asyncio


async def test_registration(session, register, make_request):
    user = {
        "email": fake.email(),
        "password": fake.password(),
        "full_name": fake.name(),
        "username": fake.simple_profile()["username"],
    }
    response = await register(user)
    assert response["status"] == http.HTTPStatus.OK

    response = await register(user)
    assert response["status"] == http.HTTPStatus.BAD_REQUEST


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
async def test_register_validation(register, user):
    response = await register(user)
    assert response["status"] == http.HTTPStatus.UNPROCESSABLE_ENTITY
