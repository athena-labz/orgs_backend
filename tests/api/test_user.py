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

    register_body = specs.RegisterBodySpec(
        user_type=specs.UserType.STUDENT,
        email="register@email.com",
        stake_address=stake_address,
        signature=signature,
    )

    register_body = {
        "user_type": "student",
        "email": "register@email.com",
        "stake_address": stake_address,
        "signature": signature
    }
    response = client.post("/users/register", json=register_body)

    assert response.status_code == 200
    user_response = response.json()

    # Make sure user was created
    user_created = await User.filter(email="register@email.com").first()
    assert user_created is not None