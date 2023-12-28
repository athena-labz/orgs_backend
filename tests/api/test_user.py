from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.model import User
from app import specs


@freeze_time("2023-12-27 15:00:00")
async def test_register():
    client = TestClient(app)

    stake_address = "stake1u88fkp0lf0txnslsk4a26l5u7p4f3enah0t7e4v63795hygh70tj7"
    signature = "a40101032720062158204a4271123edbd112632931c678080f46ed14760b5ea1636b6b2412f3d803b064H1+DFJCghAmokzYG84582aa201276761646472657373581de1ce9b05ff4bd669c3f0b57aad7e9cf06a98e67dbbd7ecd59a8f8b4b91a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638383938385840f803aa04ab411c65606f3c6db12f3f0b86751ea2cad84672285235baf0d45998cbb57a873244408094e496ce414f196377beec56874168d6926320f118ead107"

    register_body = {
        "user_type": "student",
        "email": "register@email.com",
        "stake_address": stake_address,
        "signature": signature,
    }
    response = client.post("/users/register", json=register_body)

    assert response.status_code == 200

    # Make sure user was created
    user_created = await User.filter(email="register@email.com").first()
    assert user_created is not None


@freeze_time("2023-12-28 15:00:00")
async def test_login():
    client = TestClient(app)

    stake_address = "stake1uy3fz3akmq0r9y209pxwh0lwtdwyk4gqwmgrnhd47r2cuvsvnmal7"
    signature = "a401010327200621582032f148b82ab3066577623995e74af2d65f6e8a2155fe4064b43aa1b72072ef98H1+DFJCghAmokzYG84582aa201276761646472657373581de1229147b6d81e32914f284cebbfee5b5c4b550076d039ddb5f0d58e32a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303337373339323958401e3564bec94a53488719ebbff0eec0ddce275fd4f667b6fddda11a04bc1468c1c117a49cb13263c26da03d38d68330d99a75da551ae26133237e88c4b32fc40b"

    await User.create(
        type="student",
        email="test_login@email.com",
        stake_address=stake_address,
    )

    register_body = {"username": stake_address, "password": signature}
    response = client.post("/token", data=register_body)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eTNmejNha21xMHI5eTIwOXB4d2gwbHd0ZHd5azRncXdtZ3JuaGQ0N3IyY3V2c3ZubWFsNyIsImV4cCI6MTcwMzg2MjAwMH0.y4B4aczvi6mCoq21KxcsRBm7ZQlAobOfcXgoml5wc7g",
        "token_type": "bearer",
    }