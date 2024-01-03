from fastapi.testclient import TestClient
from freezegun import freeze_time

from tortoise.expressions import Q

from app.main import app
from app.model import Organization, OrganizationMembership, User, Group, GroupMembership

import datetime


@freeze_time("2023-12-27 15:00:00")
async def test_group_create():
    test_identifier = "test_group_create"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u8u5xw9r9qntnusjqg4eaqcu45zezg9eljhs5z9w4guhd8q8cnjty"
    signature = "a40101032720062158209b88b98301f5c3f87392edcd20a1ac36527d69aafca3b961e413cbc274d5c721H1+DFJCghAmokzYG84582aa201276761646472657373581de1f94338a32826b9f212022b9e831cad059120b9fcaf0a08aeaa39769ca166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058406b9bcd3cc12d42d1e40a840bea7038cce3bcbbce6fc836f04fcb45a9babd8a36d951c4e777d6765b21b6c9861462bc8d1cebb6637c7d38ee1a9dd57ca94fc908"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OHU1eHc5cjlxbnRudXNqcWc0ZWFxY3U0NXplemc5ZWxqaHM1ejl3NGd1aGQ4cThjbmp0eSIsImV4cCI6NjE3MDM2ODkyMDB9.QwgiH4SGaUyVrorJQXVGCrA5Kl9r3E7vGtKf8xTtUgQ"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    alice_stake_address = "stake1uympaf8fhmmngvt9m6ekr3884fvjapdj4ta596y2z4yvh2c429v6k"
    alice_signature = "a4010103272006215820d23af20c50c6b7906a5ad5d708a673824ef41da8271978cf98f16a295400b730H1+DFJCghAmokzYG84582aa201276761646472657373581de1361ea4e9bef7343165deb361c4e7aa592e85b2aafb42e88a1548cbaba166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840876deca4b7d3417b922bcc7680b32ee96eba0dc8f06a67211b17e97ca08b077051127de3e005d92ded0da3b787d9e1bbf065bbb7dff1987f26e5d8b18f750307"
    alice_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eW1wYWY4ZmhtbW5ndnQ5bTZla3IzODg0ZnZqYXBkajR0YTU5NnkyejR5dmgyYzQyOXY2ayIsImV4cCI6NjE3MDM2ODkyMDB9.5nhE1so0VRqCbudLyqMjRrC808fDUUVA-quWbl0x6ps"

    alice_email = f"{test_identifier}_alice@email.com"
    alice_user = await User.create(
        type="student",
        email=alice_email,
        stake_address=alice_stake_address,
        active=True,
    )

    bob_stake_address = "stake1u9dflram8yr546pd9x2smk4u6wey8729vry4zz90jptdmtc36wc8r"
    bob_signature = "a40101032720062158206242461f7d7e9c9baac52f84566ed9ae4361a34d70610e1d29c61ed36170fb14H1+DFJCghAmokzYG84582aa201276761646472657373581de15a9f8fbb39074ae82d29950ddabcd3b243f94560c95108af9056ddafa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584062d5655bc37eddaa87cf0434abc811e8c41ae0c5c63ae20f13c6c56026546af1fa2fa01d83a7d79b9c80a3757a997bed0993958aa76efa28bada8daadf50a50a"
    bob_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OWRmbHJhbTh5cjU0NnBkOXgyc21rNHU2d2V5ODcyOXZyeTR6ejkwanB0ZG10YzM2d2M4ciIsImV4cCI6NjE3MDM2ODkyMDB9.CyL-iMx6J_Hv7gCQAY2j_bdoXly1-JDQL2kpUXPi5uo"

    bob_email = f"{test_identifier}_bob@email.com"
    bob_user = await User.create(
        type="student",
        email=bob_email,
        stake_address=bob_stake_address,
        active=True,
    )

    charlie_stake_address = (
        "stake1ux99vad3v8334wx5qcyz7mjhwkrz9xt9fn23dzk4j2sanvqpuz7vd"
    )
    charlie_signature = "a4010103272006215820cb972f457ad07ddeb7968fc891d0ad184a0ee21d2fa6419611c6b82b0564e937H1+DFJCghAmokzYG84582aa201276761646472657373581de18a5675b161e31ab8d406082f6e5775862299654cd5168ad592a1d9b0a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840578a1aa83d58ae793a66364e869fb67c1bdd884400ca409d1f370633d8c53c6733d5b9c191ad3e93d0f491f32140a8d7481dfefe70d8b1a766d479061262a305"
    charlie_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eDk5dmFkM3Y4MzM0d3g1cWN5ejdtamh3a3J6OXh0OWZuMjNkems0ajJzYW52cXB1ejd2ZCIsImV4cCI6NjE3MDM2ODkyMDB9.8ywvc679api9jF-P8FLohar6bZSo3Kuxu5sbESxqdD4"

    charlie_email = f"{test_identifier}_charlie@email.com"
    charlie_user = await User.create(
        type="student",
        email=charlie_email,
        stake_address=charlie_stake_address,
        active=True,
    )

    david_stake_address = "stake1uyj72xp3cng4j3zyaen3433435p048dkfh5q6xvwdztnlpgx9n45c"
    david_signature = "a401010327200621582018557f61bc4fb8c917419cafd4226a7c3db4f7aad4d535738c17cdf1179bc77dH1+DFJCghAmokzYG84582aa201276761646472657373581de125e51831c4d1594444ee671ac6358d02fa9db64de80d198e68973f85a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584073d209622240290d99d5d9f4c996fab590766fc871ea3bdad9bb4054db29392e1dad780820ef0825e4c030efe74d8a56ac8046651ab3b8b19c712f6884a44506"
    david_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eWo3MnhwM2NuZzRqM3p5YWVuMzQzMzQzNXAwNDhka2ZoNXE2eHZ3ZHp0bmxwZ3g5bjQ1YyIsImV4cCI6NjE3MDM2ODkyMDB9.fjd5qQD8So1Ks_F6sdjwZjQaNpw1ZuqQkTM2dtJ5OGU"

    david_email = f"{test_identifier}_david@email.com"
    david_user = await User.create(
        type="student",
        email=david_email,
        stake_address=david_stake_address,
        active=True,
    )

    created_organization = await Organization.create(
        identifier=f"{test_identifier}_org_1",
        name=f"{test_name} Org 1",
        description="",
        students_password="pass123",
        teachers_password="pass123",
        supervisor_password="pass123",
        areas=["math"],
        admin=created_user,
    )

    other_organization = await Organization.create(
        identifier=f"{test_identifier}_org_2",
        name=f"{test_name} Org 2",
        description="",
        students_password="pass123",
        teachers_password="pass123",
        supervisor_password="pass123",
        areas=["math"],
        admin=created_user,
    )

    await OrganizationMembership.create(
        user=alice_user,
        organization=created_organization,
        area="math",
    )

    await OrganizationMembership.create(
        user=bob_user,
        organization=created_organization,
        area="math",
    )

    await OrganizationMembership.create(
        user=charlie_user,
        organization=created_organization,
        area="math",
    )

    # David member of other organization
    await OrganizationMembership.create(
        user=david_user,
        organization=other_organization,
        area="math",
    )

    # Try to create group not being member of the organization
    response = client.post(
        f"/organization/{test_identifier}_org_1/group/create",
        json={
            "identifier": f"{test_identifier}_group_1",
            "name": f"{test_name} Group 1",
            "members": [bob_email, charlie_email],
        },
        headers={"Authorization": "Bearer " + david_token},
    )

    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/group/create",
        json={
            "identifier": f"{test_identifier}_group_1",
            "name": f"{test_name} Group 1",
            "members": [bob_email, charlie_email],
        },
        headers={"Authorization": "Bearer " + alice_token},
    )

    assert response.status_code == 200

    # Make sure group was created

    created_group = await Group.filter(identifier=f"{test_identifier}_group_1").first()
    assert created_group is not None

    members = (
        await GroupMembership.filter(group=created_group).prefetch_related("user").all()
    )
    assert len(members) == 3

    assert members[0].user == alice_user
    assert members[0].leader == True
    assert members[0].accepted == True
    assert members[0].rejected == False

    assert members[1].user == bob_user
    assert members[1].leader == False
    assert members[1].accepted == False
    assert members[1].rejected == False

    assert members[2].user == charlie_user
    assert members[2].leader == False
    assert members[2].accepted == False
    assert members[2].rejected == False

    # TODO: Should be able to create group as organizer or supervisor


@freeze_time("2023-12-27 15:00:00")
async def test_group_accept():
    test_identifier = "test_group_accept"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uxpeelca7p9xu5ccvm3he7xur4nje0u4qqlms7w6w6jfczgzpqgx3"
    signature = "a4010103272006215820bb5b71dc302c7b6d864c789d67ec6cb54aafd648f8a34f1366f6c0b8a34dbf60H1+DFJCghAmokzYG84582aa201276761646472657373581de1839cff1df04a6e531866e37cf8dc1d672cbf95003fb879da76a49c09a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058403a84c5f10a9061ab2caff87bcfa3951a1606e846def09c5ab5d890b96a9280c963ec0412cc1e53427d63267adf60f662179158713ddbba42945502205c189803"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eHBlZWxjYTdwOXh1NWNjdm0zaGU3eHVyNG5qZTB1NHFxbG1zN3c2dzZqZmN6Z3pwcWd4MyIsImV4cCI6NjE3MDM2ODkyMDB9.BgcCZ6VhFuACKUqfQzr7dN2RL4gTXFN4LsAvt0jR5Mo"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    other_stake_address = "stake1u828yl482f2sm0y0yd3ch0l8ph9nryeevp2nck9w59avvegj65ehy"
    other_signature = "a4010103272006215820336078e379f1e4b3e753cf48a577b428fad8aa1a78e98853993648b9d6830500H1+DFJCghAmokzYG84582aa201276761646472657373581de1d4727ea752550dbc8f23638bbfe70dcb31933960553c58aea17ac665a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840358a1c2ddc7a2cd8dc6d837f3291e4f23a3677aae3367e483baea146ebc267f575048b9d0797879bde22bab4ef67194751127a7722b33c58a4a2592a50fd1203"
    other_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1ODI4eWw0ODJmMnNtMHkweWQzY2gwbDhwaDlucnllZXZwMm5jazl3NTlhdnZlZ2o2NWVoeSIsImV4cCI6NjE3MDM2ODkyMDB9.Ofe-GKQxptwOYNwrRx_mAnj68grcPppk4a-9cVpVWs8"

    other_email = f"{test_identifier}_other@email.com"
    other_user = await User.create(
        type="student",
        email=other_email,
        stake_address=other_stake_address,
        active=True,
    )

    wrong_stake_address = "stake1u99whh0ngmjqukmv4yrdqcqly64vg4ujpjt8gfzcylvefhgy6xcjw"
    wrong_signature = "a40101032720062158208f8a9dfa91ef414386c614800f9c0e79183e137110e2ce2a723a5efefdeebe4cH1+DFJCghAmokzYG84582aa201276761646472657373581de14aebddf346e40e5b6ca906d0601f26aac457920c9674245827d994dda166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840fa89b3712335845c9469e904de89d1b88872f3f635449e74622d5e30afa1f3cd8b676c90205d76002587c2af7d723fd8ba8734de04289ab3134868a7f6b4a00e"
    wrong_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OTl3aGgwbmdtanF1a212NHlyZHFjcWx5NjR2ZzR1anBqdDhnZnpjeWx2ZWZoZ3k2eGNqdyIsImV4cCI6NjE3MDM2ODkyMDB9.-1oPR8bJWZAByyeFM59pL_YS7GYAnl8cWwcBiICMvH4"

    wrong_email = f"{test_identifier}_wrong@email.com"
    wrong_user = await User.create(
        type="student",
        email=wrong_email,
        stake_address=wrong_stake_address,
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

    await OrganizationMembership.create(
        user=created_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=other_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=wrong_user,
        organization=created_organization,
        area=None,
    )

    created_group = await Group.create(
        identifier=f"{test_identifier}_group_1",
        name=f"{test_name} Group 1",
        organization=created_organization,
    )

    await GroupMembership.create(
        group=created_group,
        user=created_user,
        accepted=True,
        leader=True,
        invite_date=datetime.datetime(2024, 1, 1),
    )

    await GroupMembership.create(
        group=created_group,
        user=other_user,
        accepted=False,
        leader=False,
        invite_date=datetime.datetime(2024, 1, 1),
    )

    # Try to accept invite when is already accepted
    response = client.post(
        f"/organization/{test_identifier}_org_1/group/{test_identifier}_group_1/accept",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 400

    # Try to accept invite when was not invited
    response = client.post(
        f"/organization/{test_identifier}_org_1/group/{test_identifier}_group_1/accept",
        headers={"Authorization": "Bearer " + wrong_token},
    )

    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/group/{test_identifier}_group_1/accept",
        headers={"Authorization": "Bearer " + other_token},
    )

    assert response.status_code == 200

    membership = await GroupMembership.filter(
        Q(group=created_group) & Q(user=other_user)
    ).first()
    assert membership is not None
    assert membership.accepted == True


@freeze_time("2023-12-27 15:00:00")
async def test_group_reject():
    test_identifier = "test_group_reject"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u9lfp58xahvkr66esqtsru93k9jv8h4zacdfk9r633xnm9gyg932c"
    signature = "a40101032720062158202d1830da8a2d2deb6596ed5118ce784db39aada63e652326a06a176a54d45738H1+DFJCghAmokzYG84582aa201276761646472657373581de17e90d0e6edd961eb59801701f0b1b164c3dea2ee1a9b147a8c4d3d95a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840d34c7d25a1d5ffc93251984c9852433d084b459ef8f5a2ec169f50653d0bf3d33f736f0c6ef61b807987ee382fa7968b27110e7d14a006183bfb8b85ea063c07"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OWxmcDU4eGFodmtyNjZlc3F0c3J1OTNrOWp2OGg0emFjZGZrOXI2MzN4bm05Z3lnOTMyYyIsImV4cCI6NjE3MDM2ODkyMDB9.i6jDkcNURiEHdmo-Ff_H2FmUm-mqPDjW4hmgCv3CHPk"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    other_stake_address = "stake1uxu5xar3epakr9sry53j7d68qvx27d9cc5dawr94947y08c5yx45x"
    other_signature = "a40101032720062158208bb76bd7f16da83e22dfd814fa3477f83bc612723bf7338d0934a4c0104ad5caH1+DFJCghAmokzYG84582aa201276761646472657373581de1b9437471c87b61960325232f3747030caf34b8c51bd70cb52d7c479fa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058402441860f9c9714e34748234e0f908a3c94f33e4b6a028ffb703305b0ae15b41f757d671767890ba405d6c1a1ad46c9a1fbe82249cb1a6659e08dc9a251c13c08"
    other_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eHU1eGFyM2VwYWtyOXNyeTUzajdkNjhxdngyN2Q5Y2M1ZGF3cjk0OTQ3eTA4YzV5eDQ1eCIsImV4cCI6NjE3MDM2ODkyMDB9.5iMjzDNu7fUnV5VrZjJdrqLUBo8n5TSWAkqIc-JSboc"

    other_email = f"{test_identifier}_other@email.com"
    other_user = await User.create(
        type="student",
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

    await OrganizationMembership.create(
        user=created_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=other_user,
        organization=created_organization,
        area=None,
    )

    created_group = await Group.create(
        identifier=f"{test_identifier}_group_1",
        name=f"{test_name} Group 1",
        organization=created_organization,
    )

    await GroupMembership.create(
        group=created_group,
        user=created_user,
        accepted=True,
        leader=True,
        invite_date=datetime.datetime(2024, 1, 1),
    )

    await GroupMembership.create(
        group=created_group,
        user=other_user,
        accepted=False,
        leader=False,
        invite_date=datetime.datetime(2024, 1, 1),
    )

    # Try to reject invite when is already accepted
    response = client.post(
        f"/organization/{test_identifier}_org_1/group/{test_identifier}_group_1/reject",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/group/{test_identifier}_group_1/reject",
        headers={"Authorization": "Bearer " + other_token},
    )

    assert response.status_code == 200

    membership = await GroupMembership.filter(
        Q(group=created_group) & Q(user=other_user)
    ).first()
    assert membership is not None
    assert membership.rejected == True


@freeze_time("2023-12-27 15:00:00")
async def test_group_leave():
    test_identifier = "test_group_leave"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uytd6lp88q3753xwe509ml2c49gyrnk26as9hx38xlcs2lgk60awl"
    signature = "a40101032720062158209a239908e601ee9d4dc9d91c07dae32b4037545417b0617db94f025629fd0233H1+DFJCghAmokzYG84582aa201276761646472657373581de116dd7c273823ea44cecd1e5dfd58a95041cecad7605b9a2737f1057da166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840df36bc4ee32fc56dc2dec4e29f82891bc4c8332dbfdeade3348ae9f7cdee8165e61f46be6c471d2d2a1833c4acae1fdef17e642453fc25bd415ca42e09da980a"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eXRkNmxwODhxMzc1M3h3ZTUwOW1sMmM0OWd5cm5rMjZhczloeDM4eGxjczJsZ2s2MGF3bCIsImV4cCI6NjE3MDM2ODkyMDB9.X2paHb30FjtIRavNCM72TC5NPZnqUFyNIUZDZnXDcPs"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    other_stake_address = "stake1u94hrz3py6ku0vyygwr3prquard5xgwka6zy39ln90m0slgq33ffy"
    other_signature = "a40101032720062158202cdce64819bb90c34838576791e899f9252e76753a422ad88a44a6a0820be5b1H1+DFJCghAmokzYG84582aa201276761646472657373581de16b718a2126adc7b0844387108c1ce8db4321d6ee844897f32bf6f87da166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840b81b71e2ef84fc35f3b415629831a099a279124141c8abd9501c4a8336b2592fd0b9008605677c91acfaa2dd9c63ccc7c4fbd8bf14e1b9c7411ff87e7d48120e"
    other_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OTRocnozcHk2a3Uwdnl5Z3dyM3BycXVhcmQ1eGd3a2E2enkzOWxuOTBtMHNsZ3EzM2ZmeSIsImV4cCI6NjE3MDM2ODkyMDB9.rTPxyNDsiNc9YgHFxpvjAztOJz0VS3RoMLjBqsXPiHE"

    other_email = f"{test_identifier}_other@email.com"
    other_user = await User.create(
        type="student",
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

    await OrganizationMembership.create(
        user=created_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=other_user,
        organization=created_organization,
        area=None,
    )

    created_group = await Group.create(
        identifier=f"{test_identifier}_group_1",
        name=f"{test_name} Group 1",
        organization=created_organization,
    )

    await GroupMembership.create(
        group=created_group,
        user=created_user,
        accepted=True,
        leader=True,
        invite_date=datetime.datetime(2024, 1, 1),
    )

    await GroupMembership.create(
        group=created_group,
        user=other_user,
        accepted=True,
        leader=False,
        invite_date=datetime.datetime(2024, 1, 1),
    )

    # Try to leave as a leader
    response = client.post(
        f"/organization/{test_identifier}_org_1/group/{test_identifier}_group_1/leave",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/group/{test_identifier}_group_1/leave",
        headers={"Authorization": "Bearer " + other_token},
    )

    print(response.json())
    assert response.status_code == 200

    membership = await GroupMembership.filter(
        Q(group=created_group) & Q(user=other_user)
    ).first()
    assert membership is not None
    assert membership.rejected == True
