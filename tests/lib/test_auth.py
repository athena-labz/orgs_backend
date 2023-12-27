from fastapi.testclient import TestClient

from app.lib import auth
from app.model import User
from freezegun import freeze_time

import pycardano as pyc
import datetime
import pytest


@pytest.mark.asyncio
@freeze_time("2023-12-27 14:43:00")
async def test_authenticate_user():
    # monkeypatch.setenv("USER", "TestingUser")

    right_stake_address = "stake1uymfqdggvdrauqfh36jm4us9ac5pm7n9hj68gj8mf2pfjlscj8s0c"
    signature = "a4010103272006215820a7823182f1b024de887bf1063f5a1dbfaa8df39aa6699c3904121c2db7124f67H1+DFJCghAmokzYG84582aa201276761646472657373581de1369035086347de01378ea5baf205ee281dfa65bcb47448fb4a82997ea166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363837383832584026b7c67ee6691cd84550993d76880bd8aeaaef941c925ec0691561ee762c53caf4e8c28d7056a4946604187e10884e041dee5f0023f6bd1f7c480ac8c82be50f"

    # Should return None since there is no User
    user = await auth.authenticate_user(right_stake_address, signature)
    assert user is None

    user_created = await User.create(
        type="type", email="alice@email.com", stake_address=right_stake_address
    )

    user_authenticated = await auth.authenticate_user(right_stake_address, signature)
    assert user_created == user_authenticated


@pytest.mark.asyncio
async def test_has_review_privileges():
    student = await User.create(
        type="student", email="bob@email.com", stake_address="stake456"
    )

    teacher = await User.create(
        type="teacher", email="charlie@email.com", stake_address="stake789"
    )

    organizer = await User.create(
        type="organizer", email="david@email.com", stake_address="stakeabc"
    )

    supervisor = await User.create(
        type="supervisor", email="emma@email.com", stake_address="stakedef"
    )

    assert auth.has_review_privileges(student) is False
    assert auth.has_review_privileges(teacher) is True
    assert auth.has_review_privileges(organizer) is True
    assert auth.has_review_privileges(supervisor) is True