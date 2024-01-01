from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.model import Organization, User
from app import specs


@freeze_time("2023-12-27 15:00:00")
async def test_organization_create():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_organization_edit():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_organization_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_organization_join():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_organization_areas_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_organization_tasks_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_organization_users_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_organization_groups_read():
    client = TestClient(app)

    assert False
