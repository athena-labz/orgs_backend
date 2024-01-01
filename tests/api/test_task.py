from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.model import Organization, User, Group, Task
from app import specs


@freeze_time("2023-12-27 15:00:00")
async def test_task_create():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_members_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_actions_read():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_start_approve():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_start_reject():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_create():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_approve():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_reject():
    client = TestClient(app)

    assert False


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_review():
    client = TestClient(app)

    assert False