from app.main import app

from fastapi.testclient import TestClient
from tortoise import Tortoise

import asyncio
import pytest

DB_URL = "sqlite://:memory:"


async def init_db():
    """Initial database connection"""

    await Tortoise.init(
        db_url=DB_URL, modules={"models": ["app.model"]}, _create_db=True
    )

    await Tortoise.generate_schemas()


async def init():
    await init_db()


@pytest.fixture(scope="session")
async def client():
    client = TestClient(app)
    with client as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    await init()

    yield

    await Tortoise.close_connections()


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop

    loop.close()
