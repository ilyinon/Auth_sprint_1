import aiohttp
import pytest
import pytest_asyncio

from tests.functional.settings import test_settings


@pytest_asyncio.fixture
async def register(make_request):
    async def inner(json: dict) -> dict:
        return await make_request(
            aiohttp.hdrs.METH_POST, "/api/v1/auth/signup", json=json
        )

    return inner


@pytest.fixture
def make_request(session: aiohttp.ClientSession):
    async def inner(
        method: str,
        endpoint: str,
        params: dict = {},
        json: dict = {},
        headers: dict = {},
    ):
        url = f"{test_settings.app_dsn}{endpoint}"
        async with session.request(
            method, url, params=params, json=json, headers=headers
        ) as response:
            return {
                "status": response.status,
                "headers": response.headers,
                "body": await response.json(),
            }

    return inner
