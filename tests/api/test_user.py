from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.model import (
    User,
    UserBalance,
    Organization,
    OrganizationMembership,
    Task,
    Group,
    GroupMembership,
)
from app import specs

import datetime


@freeze_time("2023-12-27 15:00:00")
async def test_user_register():
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
async def test_user_login():
    client = TestClient(app)

    stake_address = "stake1uy3fz3akmq0r9y209pxwh0lwtdwyk4gqwmgrnhd47r2cuvsvnmal7"
    signature = "a401010327200621582032f148b82ab3066577623995e74af2d65f6e8a2155fe4064b43aa1b72072ef98H1+DFJCghAmokzYG84582aa201276761646472657373581de1229147b6d81e32914f284cebbfee5b5c4b550076d039ddb5f0d58e32a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303337373339323958401e3564bec94a53488719ebbff0eec0ddce275fd4f667b6fddda11a04bc1468c1c117a49cb13263c26da03d38d68330d99a75da551ae26133237e88c4b32fc40b"

    await User.create(
        type="student",
        email="test_login@email.com",
        stake_address=stake_address,
    )

    register_body = {"username": stake_address, "password": signature}
    response = client.post("/users/login", data=register_body)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eTNmejNha21xMHI5eTIwOXB4d2gwbHd0ZHd5azRncXdtZ3JuaGQ0N3IyY3V2c3ZubWFsNyIsImV4cCI6MTcwMzg2MjAwMH0.y4B4aczvi6mCoq21KxcsRBm7ZQlAobOfcXgoml5wc7g",
        "token_type": "bearer",
    }


@freeze_time("2023-12-27 15:00:00")
async def test_user_confirm_email():
    client = TestClient(app)

    stake_address = "stake1uxc9jqd8kkfzgs98thtlpmqkz6gngf064gs3zj9nl6gjj4gqes0sq"
    signature = "a40101032720062158208eb44e0e4cb9e35aff24d77da9c46ee3a9495b29120826e6c741d0581f344de4H1+DFJCghAmokzYG84582aa201276761646472657373581de1b05901a7b5922440a75dd7f0ec1616913425faaa211148b3fe912955a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840045c07dcd0f1f90d7d8d17b6b3eb6b7ac89027d698385e509cc2568e7dafc5950f39e061dbbf04906f2d7cde7d627f5877c9fb8bfe4f0f2b2fa017f5f38d6800"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eGM5anFkOGtrZnpnczk4dGh0bHBtcWt6NmduZ2YwNjRnczN6ajlubDZnamo0Z3FlczBzcSIsImV4cCI6MTcwMzc3NTYwMH0._D5PHouMzoX6kHtib484v6D7UsM_j9X6301Q0HOP-Sw"

    await User.create(
        type="student",
        email="test_user_confirm_email@email.com",
        stake_address=stake_address,
        active=False,
        email_validation_string="test123",
    )

    response = client.post(
        "/users/me/email/confirm",
        headers={"Authorization": "Bearer " + token},
        params={"email_validation_string": "test123"},
    )

    assert response.status_code == 200

    user = await User.filter(email="test_user_confirm_email@email.com").first()

    assert user is not None
    assert user.active is True


@freeze_time("2023-12-27 15:00:00")
async def test_user_payment_address_add():
    test_identifier = "test_user_payment_address_add"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u83pehgnhut7scn6n0pm3uzr7maxll4dn0y27m6lgmrlavgqq7dhl"
    signature = "a4010103272006215820fe531877d83d4e0d9227ea009ea31979bdfc02055e95f7971870e71a4344a0e2H1+DFJCghAmokzYG84582aa201276761646472657373581de1e21cdd13bf17e8627a9bc3b8f043f6fa6ffead9bc8af6f5f46c7feb1a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840b50460e6d415e6251dd55d8a21c08c038df5534afee34748105f22080c3c6be9dbf3cb85b48baaa278d970b69a408b128a2af401435140ee2727a8d758df3b0b"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1ODNwZWhnbmh1dDdzY242bjBwbTN1enI3bWF4bGw0ZG4weTI3bTZsZ21ybGF2Z3FxN2RobCIsImV4cCI6NjE3MDM2ODkyMDB9.bYnpGP5gPngcT2aFjxxXQSMJI4uTLGAc-42DFbulvzI"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    response = client.post(
        "/users/me/address/add",
        json={"address": "addr1vy9nwdp3p7tnnxwrz4ya8lcejr4nw6xndhc6k69xq3kaprg5jumfq"},
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200

    # Find user
    user = await User.filter(stake_address=stake_address).first()

    assert user is not None
    assert (
        user.payment_address
        == "addr1vy9nwdp3p7tnnxwrz4ya8lcejr4nw6xndhc6k69xq3kaprg5jumfq"
    )


@freeze_time("2023-12-28 15:00:00")
async def test_user_read():
    client = TestClient(app)

    stake_address = "stake1uxc4fxd6r4rjgm38aqlkac85vu5arvm6q8m3wmy43h0h3dcs9dvnu"
    signature = "a4010103272006215820daa3c23a81fe0388077ed23f016b61488af35ed73ce066d564404980a241b25eH1+DFJCghAmokzYG84582aa201276761646472657373581de1b15499ba1d47246e27e83f6ee0f46729d1b37a01f7176c958ddf78b7a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333737353030365840b5726a056c1d936f85fd2c30193d7cfaa1d66aff6fc3668945ed7700685fa8cc21c703a5c1077b0b0a5df1e1174f42bf73401b2905fb24535e30c4a3834f7401"

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eGM0ZnhkNnI0cmpnbTM4YXFsa2FjODV2dTVhcnZtNnE4bTN3bXk0M2gwaDNkY3M5ZHZudSIsImV4cCI6MTcwMzg2MjAwMH0.wk-OQKV8fWu6anT9tsCTd7XEgqTLM3w6SSWAsErBtOU"

    await User.create(
        type="student",
        email="test_get_user@email.com",
        stake_address=stake_address,
        active=True,
    )

    response = client.get("/users/me", headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200
    assert (
        response.json().items()
        >= {
            "type": "student",
            "email": "test_get_user@email.com",
            "stake_address": "stake1uxc4fxd6r4rjgm38aqlkac85vu5arvm6q8m3wmy43h0h3dcs9dvnu",
            "active": True,
        }.items()
    )


@freeze_time("2023-12-27 15:00:00")
async def test_user_organizations_read():
    client = TestClient(app)

    stake_address = "stake1ux9f8w0dxr47ktx990yescw666snap6uvlhzrv663p6ufhgu2zwuc"
    signature = "a4010103272006215820c1b45f0058e3cd113f765a6f04d46630195ee79ff655a74104abfab95484b7bfH1+DFJCghAmokzYG84582aa201276761646472657373581de18a93b9ed30ebeb2cc52bc99861dad6a13e875c67ee21b35a8875c4dda166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840fe439ada5c7e42e9cc8af758d6f45faec3612ab1518b0348ac2f11ecb6da4740e93b3af5520ebec3c61d9df6be87818afe9102ad5399ea9da17d42a9d2342608"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eDlmOHcwZHhyNDdrdHg5OTB5ZXNjdzY2NnNuYXA2dXZsaHpydjY2M3A2dWZoZ3Uyend1YyIsImV4cCI6MTcwMzc3NTYwMH0.LNkHkIX7tScGMZYGVs-3XRdvg8czPxCmDITpDB_bzIA"

    created_user = await User.create(
        type="student",
        email="test_user_organizations_read@email.com",
        stake_address=stake_address,
        active=True,
    )

    created_organization = await Organization.create(
        identifier="user_organizations_read_org_1",
        name="User Organizations Read Org 1",
        description="",
        students_password="pass123",
        teachers_password="pass123",
        supervisor_password="pass123",
        areas=[],
        admin=created_user,
    )

    await OrganizationMembership.create(
        user=created_user,
        organization=created_organization,
        area=None,
    )

    response = client.get(
        "/users/me/organizations", headers={"Authorization": "Bearer " + token}
    )

    assert response.status_code == 200
    assert response.json()["current_page"] == 1
    assert response.json()["max_page"] == 1

    assert isinstance(response.json()["organizations"], list)
    assert len(response.json()["organizations"]) == 1

    assert (
        response.json()["organizations"][0].items()
        >= {
            "identifier": "user_organizations_read_org_1",
            "name": "User Organizations Read Org 1",
            "description": "",
            "supervisor_password": "pass123",
            "areas": [],
        }.items()
    )


@freeze_time("2023-12-27 15:00:00")
async def test_user_tasks_read():
    client = TestClient(app)

    stake_address = "stake1u8gau3yuxvuklt4q0jp83cdkmjp2ym9pjdf96wtvsmhueeqluxe7q"
    signature = "a40101032720062158200a300bd26dca078f8b723fc99f7334ddc662d7bab550c18de200df99bd5c3c01H1+DFJCghAmokzYG84582aa201276761646472657373581de1d1de449c33396faea07c8278e1b6dc82a26ca193525d396c86efcce4a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058406761c21d75507ac47549027d1ad149ec505e2f0881e3011994b151e1b12c500242015d2c48ba7f003db68eb592daccbc75cdfcc537d2070cc1c0ed4ea0c85b08"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OGdhdTN5dXh2dWtsdDRxMGpwODNjZGttanAyeW05cGpkZjk2d3R2c21odWVlcWx1eGU3cSIsImV4cCI6MTcwMzc3NTYwMH0.GCJ_7iSi-HSRfGeO2dhV99If65cvcTGRaboSejSonH0"

    created_user = await User.create(
        type="student",
        email="test_user_tasks_read@email.com",
        stake_address=stake_address,
        active=True,
    )

    created_organization = await Organization.create(
        identifier="test_user_tasks_read_org_1",
        name="User Tasks Read Org 1",
        description="",
        students_password="pass123",
        teachers_password="pass123",
        supervisor_password="pass123",
        areas=[],
        admin=created_user,
    )

    await OrganizationMembership.create(
        user=created_user,
        organization=created_organization,
        area=None,
    )

    created_group = await Group.create(
        identifier="test_user_tasks_read_group_1",
        name="User Tasks Read Group 1",
        organization=created_organization,
    )

    await GroupMembership.create(
        group=created_group,
        user=created_user,
        accepted=True,
        leader=True,
    )

    await Task.create(
        identifier="test_user_tasks_read_task_1",
        name="User Tasks Read Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
    )

    response = client.get(
        "/users/me/organization/test_user_tasks_read_org_1/tasks",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200

    assert response.json()["current_page"] == 1
    assert response.json()["max_page"] == 1

    assert isinstance(response.json()["tasks"], list)
    assert len(response.json()["tasks"]) == 1

    assert (
        response.json()["tasks"][0].items()
        >= {
            "identifier": "test_user_tasks_read_task_1",
            "name": "User Tasks Read Task 1",
            "description": "",
            "deadline": "2024-01-01T00:00:00Z",
            "is_approved_start": False,
            "is_rejected_start": False,
            "is_approved_completed": False,
            "is_rejected_completed": False,
            "is_rewards_claimed": False,
        }.items()
    )


@freeze_time("2023-12-27 15:00:00")
async def test_user_balance_read():
    test_identifier = "test_user_balance_read"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1ux9rs63rgvsvwzp87r8vlzzz2p78gmdyszjpyfk9fy9sxac2zzrrc"
    signature = "a40101032720062158209add2f255d6ce14a36501ee2700ba16ae542eddcc85a8e2273aa38ccab6e3eb8H1+DFJCghAmokzYG84582aa201276761646472657373581de18a386a234320c70827f0cecf8842507c746da480a41226c5490b0377a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058403b8ce1367d26483d28f9a6b51aff7d32dfb4379df1d3e82a614f5ad5f96292a6e82bf9dfaffbb57eba1a07ca0c890718c81fa9017a69a55ea6ad6cc52203ec07"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eDlyczYzcmd2c3Z3enA4N3I4dmx6enoycDc4Z21keXN6anB5Zms5Znk5c3hhYzJ6enJyYyIsImV4cCI6NjE3MDM2ODkyMDB9.MW3ATMetvoSi2OjybdOMQuiWi4oZWMZ1rwcCJB2o-BE"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    other_email = f"{test_identifier}_other@email.com"
    other_stake_address = "stake1ux9lnxds60hdyg7r6p9za5d0k5a8rk72jyelveqqkdre3fc4pqr26"
    other_user = await User.create(
        type="organizer",
        email=other_email,
        stake_address=other_stake_address,
        active=True,
    )

    created_organization = await Organization.create(
        identifier=f"{test_identifier}_org_1",
        name=f"{test_name} Org 1",
        description="",
        students_password="pass123",
        teachers_password="pass123",
        supervisor_password="pass123",
        areas=[],
        admin=created_user,
    )

    created_membership = await OrganizationMembership.create(
        user=created_user,
        organization=created_organization,
        area=None,
    )

    other_membership = await OrganizationMembership.create(
        user=other_user,
        organization=created_organization,
        area=None,
    )

    await UserBalance.create(
        amount=3_000_000,
        is_claimed=False,
        user_member=created_membership,
    )

    await UserBalance.create(
        amount=5_000_000,
        is_claimed=False,
        is_escrowed=True,
        user_member=created_membership,
    )

    await UserBalance.create(
        amount=7_000_000,
        is_claimed=True,
        user_member=created_membership,
        claim_date=datetime.datetime(2024, 1, 5),
    )

    await UserBalance.create(
        amount=1_000_000,
        is_claimed=True,
        user_member=created_membership,
        claim_date=datetime.datetime(2024, 1, 3),
    )

    await UserBalance.create(
        amount=6_000_000, is_claimed=False, user_member=other_membership
    )

    await UserBalance.create(
        amount=2_000_000, is_claimed=False, user_member=created_membership
    )

    response = client.get(
        f"/users/me/organization/{test_identifier}_org_1/balance",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200
    assert response.json() == {
        "owed": 10_000_000,
        "available": 5_000_000,
        "escrowed": 5_000_000,
        "claimed": 8_000_000,
        "last_claim_date": "2024-01-05T00:00:00Z",
    }
