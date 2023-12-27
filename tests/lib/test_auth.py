from fastapi.testclient import TestClient

from app.lib import auth
from app.model import User

import pycardano as pyc
import tortoise
import logging
import pytest


@pytest.mark.asyncio
async def test_authenticate_user():
    # await setup_database()

    right_stake_address = "stake1uxhmuwg0da896w7z2whljuz35xga42wgt44x4r7rhw6ty9sasf2tk"

    signature = "a401010327200621582015d28451ceae59012c70de6884a723d071f71a56115bd7f9528bbb9bab1cf008H1+DFJCghAmokzYG84582aa201276761646472657373581de1afbe390f6f4e5d3bc253aff97051a191daa9c85d6a6a8fc3bbb4b216a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638343033345840346355ddcafa829a246ec207b24bbc78e977fcc57a456f4b581be51f471910616021bfd3a3a75fa3878087b40a94a34b93f0ff3fce8c54bf1ff6b06217961f09"

    # Should return None since there is no User
    user = await auth.authenticate_user(right_stake_address, signature)
    assert user is None

    user_created = await User.create(
        type="type", email="alice@email.com", stake_address=right_stake_address
    )

    user_authenticated = await auth.authenticate_user(right_stake_address, signature)
    assert user_created == user_authenticated