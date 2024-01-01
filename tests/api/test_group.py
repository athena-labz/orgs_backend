from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.model import Organization, User, Group
from app import specs


@freeze_time("2023-12-27 15:00:00")
async def test_group_create():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_group_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_group_accept():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_group_reject():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_group_leave():
    client = TestClient(app)

    assert False