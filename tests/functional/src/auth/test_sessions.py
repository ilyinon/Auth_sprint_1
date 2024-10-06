import http

import pytest
from faker import Faker

from tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio


fake = Faker()

auth_url_template = "{service_url}/api/v1/auth/{endpoint}"
sessions_url_template = "{service_url}/api/v1/users/sessions"
session_id_url_template = "{service_url}/api/v1/users/sessions/{uuid}"


headers = {"Content-Type": "application/json"}

url_signup = auth_url_template.format(
    service_url=test_settings.app_dsn, endpoint="signup"
)
url_login = auth_url_template.format(
    service_url=test_settings.app_dsn, endpoint="login"
)
url_sessions = sessions_url_template.format(
    service_url=test_settings.app_dsn, endpoint=""
)


admin_user = {
    "email": fake.email(),
    "password": fake.password(),
    "full_name": fake.name(),
    "username": fake.simple_profile()["username"],
}

admin_login_data = {"email": admin_user["email"], "password": admin_user["password"]}


async def test_get_sessions_wo_creds(session, db_truncate):
    async with session.get(url_sessions) as response:

        assert response.status == http.HTTPStatus.UNAUTHORIZED


async def test_get_sessions(session, db_truncate):
    async with session.post(url_signup, json=admin_user) as response:

        body = await response.json()

    async with session.post(url_login, json=admin_user) as response:

        body = await response.json()
        access_token = body["access_token"]

    async with session.get(
        url_sessions, headers={"Authorization": f"Bearer {access_token}"}
    ) as response:
        body = await response.json()

    assert response.status == http.HTTPStatus.OK
    assert isinstance(body[-1]["id"], str)


async def test_delete_session_by_id(session, db_truncate):
    async with session.post(url_signup, json=admin_user) as response:

        body = await response.json()

    async with session.post(url_login, json=admin_user) as response:

        body = await response.json()
        access_token = body["access_token"]

    async with session.get(
        url_sessions, headers={"Authorization": f"Bearer {access_token}"}
    ) as response:
        body = await response.json()
        session_id = body[-1]["id"]

    url_session_id = session_id_url_template.format(
        service_url=test_settings.app_dsn, uuid=session_id
    )

    async with session.delete(
        url_session_id,
        json={"session_id": session_id},
        headers={"Authorization": f"Bearer {access_token}"},
    ) as response:
        body = await response.json()
    assert response.status == http.HTTPStatus.OK

    async with session.delete(
        url_session_id,
        json={"session_id": session_id},
        headers={"Authorization": f"Bearer {access_token}"},
    ) as response:
        body = await response.json()
    assert response.status == http.HTTPStatus.NOT_FOUND
