from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.model import (
    Organization,
    OrganizationMembership,
    User,
    Group,
    GroupMembership,
    Task,
)

import datetime

@freeze_time("2023-12-27 15:00:00")
async def test_group_task_create():
    test_identifier = "test_group_task_create"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uxe7sdw3g66nkluqcu6rlt5422j48gdtd60068jzarlq73szt6snj"
    signature = "a40101032720062158206c12d6a32bcdb1b0afdfa3428095086f03bbe044070fb12d07becb25d8c5ebc1H1+DFJCghAmokzYG84582aa201276761646472657373581de1b3e835d146b53b7f80c7343fae9552a553a1ab6e9efd1e42e8fe0f46a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840788068fbd96faba54e2c6acacec3c3bf4b09fe349305540cfbd4985bb23c53aef1dd59c92ac3fb349fe00094b3ca9b9243bb2bdf3c56369976e7f47025891e0d"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eGU3c2R3M2c2Nm5rbHVxY3U2cmx0NTQyMmo0OGdkdGQ2MDA2OGp6YXJscTczc3p0NnNuaiIsImV4cCI6NjE3MDM2ODkyMDB9.usozPlQm3w0NFRgVg8A74KeEZ6jKnUiZ9Zo4v8k5i6g"
    
    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
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

    response = client.post(
        f"/organization/{test_identifier}_org_1/group/task/create",
        json={
            "identifier": f"{test_identifier}_task_1",
            "name": f"{test_name} Task 1",
            "description": "",
            "rewards": {f"{test_identifier}@email.com": 200},
            "deadline": "2024-01-01T00:00:00Z",
        },
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200


@freeze_time("2023-12-27 15:00:00")
async def test_individual_task_create():
    test_identifier = "test_individual_task_create"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u88jffq736p8u2fkwwfy9x4rvc2sajvexhw4fje028mj9ycn5gam5"
    signature = "a40101032720062158201de17b6a9bb2f055635d54ba26b3f38dbc573a3bbbfc494d0e0ac9e24fa3aa96H1+DFJCghAmokzYG84582aa201276761646472657373581de1cf24a41e8e827e29367392429aa366150ec99935dd54cb2f51f72293a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058405bb2ee98935ddf1c38dbcbea9779bc4e1b587ebfb59b1973d7e940d4796d603403b8047d86edf27a171b199a78dc37289ff3608921e7ce0f601c147a615d310a"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1ODhqZmZxNzM2cDh1MmZrd3dmeTl4NHJ2YzJzYWp2ZXhodzRmamUwMjhtajl5Y241Z2FtNSIsImV4cCI6NjE3MDM2ODkyMDB9.4iWQp89dYCN8qY0EBHAIKFqXj2xj4mSk8mSHbslYWic"
    
    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
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

    response = client.post(
        f"/organization/{test_identifier}_org_1/task/create",
        json={
            "identifier": f"{test_identifier}_task_1",
            "name": f"{test_name} Task 1",
            "description": "...description...",
            "deadline": "2024-01-01T00:00:00Z",
        },
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200

    task = await Task.filter(identifier=f"{test_identifier}_task_1").first()

    assert task.identifier == f"{test_identifier}_task_1"
    assert task.name == f"{test_name} Task 1"
    assert task.description == "...description..."
    assert task.deadline.timestamp() == datetime.datetime(2024, 1, 1).timestamp()
    assert task.is_individual == True


@freeze_time("2023-12-27 15:00:00")
async def test_task_start_approve():
    test_identifier = "test_task_start_approve"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uykgkn4nprevlzg6eullhgjnh2slzp6gkmhnqv7q528q5gg5gsgzg"
    signature = "a4010103272006215820184e0f470c2f8eaa5ba2e82f3677f91743134b541f5157607390625cb0cdae82H1+DFJCghAmokzYG84582aa201276761646472657373581de12c8b4eb308f2cf891acf3ffba253baa1f10748b6ef3033c0a28e0a21a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058408b72db662fc52a69dff4dcfb3a60b22de8d91a5f493262c65e1cfdbc0b57b2dfac5e4aad43cba81f5fd010bc3c43aa296723bb2be1eb6d59535f82c00dd6390a"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eWtna240bnByZXZsemc2ZXVsbGhnam5oMnNsenA2Z2ttaG5xdjdxNTI4cTVnZzVnc2d6ZyIsImV4cCI6NjE3MDM2ODkyMDB9.Uts35TLT4BTioAIp9t9nWSHHT75FYe46tygfzMjIg0E"
    
    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    student_stake_address = "stake1u9ts4zgjrj4x8y8qp69w3kv4dh8wdpg5s9dnuftw4qjujmg7pnjve"
    student_signature = "a401010327200621582069dda7838119bf512ae0a463c31346b22810372e77d8da1667ed13b1b8aefd00H1+DFJCghAmokzYG84582aa201276761646472657373581de1570a89121caa6390e00e8ae8d9956dcee68514815b3e256ea825c96da166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840580ac50f740f90a07c4b46b91285ddae1933d6b27af7580f0be9fffb4a85da0bb534724de89a2def56350cc332221bec6779111b6ae34db8eadc2bf8789cd10f"
    student_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OXRzNHpnanJqNHg4eThxcDY5dzNrdjRkaDh3ZHBnNXM5ZG51ZnR3NHFqdWptZzdwbmp2ZSIsImV4cCI6NjE3MDM2ODkyMDB9._jUlyhvGCg6_T_pZpPjfXbqvXePw5a_gbxkdg9ZvkDA"
    
    student_email = f"{test_identifier}_student@email.com"
    student_user = await User.create(
        type="student",
        email=student_email,
        stake_address=student_stake_address,
        active=True,
    )

    teacher_stake_address = "stake1u8f78w7gpq06u89n4tjsdwywrcadl2nm8mdk6u6wvqwjp2cymxms3"
    teacher_signature = "a401010327200621582073b1857f193a0246d2f638f44e0dee7c2488551dc2fed6aea78ef32b2782a357H1+DFJCghAmokzYG84582aa201276761646472657373581de1d3e3bbc8081fae1cb3aae506b88e1e3adfaa7b3edb6d734e601d20aba166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840a4c90d6bed1468ec3862e036d5cda5a1fccb421880467d2e1050ecf7ab80a0d8990128cfcffc656d9fca0c41d749b7b23bf4f6d1314e74e3c79feb4208a61b02"
    teacher_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OGY3OHc3Z3BxMDZ1ODluNHRqc2R3eXdyY2FkbDJubThtZGs2dTZ3dnF3anAyY3lteG1zMyIsImV4cCI6NjE3MDM2ODkyMDB9.WGizd1fSCnm0Zip0XpbO8r_380jioYWA1OEGOyPShhM"
    
    teacher_email = f"{test_identifier}_teacher@email.com"
    teacher_user = await User.create(
        type="teacher",
        email=teacher_email,
        stake_address=teacher_stake_address,
        active=True,
    )

    supervisor_stake_address = "stake1uyrqwru6mdn7hp5tfg27929nx80h34ktyaru58pcf5xyvzcf4zjz8"
    supervisor_signature = "a4010103272006215820d65642ff730ddb1f865ace23cb8496048243680d6ea82c4dacbf052d0aea89bcH1+DFJCghAmokzYG84582aa201276761646472657373581de106070f9adb67eb868b4a15e2a8b331df78d6cb2747ca1c384d0c460ba166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584072ee49f7075009192d498bdd4a75b1887f4c48dd4d098fb290b183d14df04adc9373aa3545833e2746770c8b75f4971553f09a0b6a4fd6361495e41e1ec68e04"
    supervisor_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eXJxd3J1Nm1kbjdocDV0ZmcyNzkyOW54ODBoMzRrdHlhcnU1OHBjZjV4eXZ6Y2Y0emp6OCIsImV4cCI6NjE3MDM2ODkyMDB9.Q40vsOByeRPTref5mR7j5RicXhFUewpOc-vsAbUqdCg"
    
    supervisor_email = f"{test_identifier}_supervisor@email.com"
    supervisor_user = await User.create(
        type="supervisor",
        email=supervisor_email,
        stake_address=supervisor_stake_address,
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
        user=teacher_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=student_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=supervisor_user,
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

    created_task = await Task.create(
        identifier=f"{test_identifier}_task_1",
        name=f"{test_name} Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
    )

    # Should be able to approve as teacher, supervisor or organizer

    # Organizer
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/approve",
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_approved_start": False})
    await created_task.save()

    # Teacher
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/approve",
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_approved_start": False})
    await created_task.save()

    # Supervisor
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/approve",
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_approved_start": False})
    await created_task.save()

    # Student - not allowed
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/approve",
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400


@freeze_time("2023-12-27 15:00:00")
async def test_task_start_reject():
    test_identifier = "test_task_start_reject"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u8mvdsn3429qsn5al5rhwm3rn6wa8epvhwgu6nydaradt8gxhtchl"
    signature = "a4010103272006215820b5972c791e36cbd403cff4bc8d5714df1be40a28d4b5dec3fd665a7a6a32fdf8H1+DFJCghAmokzYG84582aa201276761646472657373581de1f6c6c271aa8a084e9dfd07776e239e9dd3e42cbb91cd4c8de8fad59da166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058402cf3ea9a94fd6b1ef56d473349a6fc913ad584f8eb60e2e2048e6bbcf62e90fd74225d6548a8a0bd381f0769b6aa85d6a755696abd4753283e6f414b6b171e07"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OG12ZHNuMzQyOXFzbjVhbDVyaHdtM3JuNndhOGVwdmh3Z3U2bnlkYXJhZHQ4Z3hodGNobCIsImV4cCI6NjE3MDM2ODkyMDB9.PexNnHHNdpF8JpQMiBVO4VLSDLxOD2mNKMu8H-b9sIY"
    
    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    student_stake_address = "stake1uxmyeqhe3yfccx0qmd46gsjmte9er0nsell32ef648jtfyq0ljrxq"
    student_signature = "a4010103272006215820bfc39005a8ae4c8ba95c3fa320a8768e35f20fd32faf22f47e12a0ea94e30bdaH1+DFJCghAmokzYG84582aa201276761646472657373581de1b64c82f989138c19e0db6ba4425b5e4b91be70cfff15653aa9e4b490a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840c21552b015406f45b62d8bdd5af7701644f7e792a20fa817b12efa44478365f2c4e7c695daef783b491c4424360ab8e37f8e2dc6db5af6913f24c971f90bdc0e"
    student_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eG15ZXFoZTN5ZmNjeDBxbWQ0Nmdzam10ZTllcjBuc2VsbDMyZWY2NDhqdGZ5cTBsanJ4cSIsImV4cCI6NjE3MDM2ODkyMDB9.hM4Y9AvhLWa6DIWFg9DFfvETFXJaODnMqnwKjbMs7VQ"
 
    student_email = f"{test_identifier}_student@email.com"
    student_user = await User.create(
        type="student",
        email=student_email,
        stake_address=student_stake_address,
        active=True,
    )

    teacher_stake_address = "stake1u94dxhmwsv62syljj6g8p0pv7kme38tl3kpxtqy9er0z7ug0evza0"
    teacher_signature = "a401010327200621582009d86c835a9dabe5a9401bef14de62283eb7595b04f89e9d20d6100a82e0230cH1+DFJCghAmokzYG84582aa201276761646472657373581de16ad35f6e8334a813f2969070bc2cf5b7989d7f8d82658085c8de2f71a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840d5d3d1578e2f95007afce10f4682fd9b23221c0be2c6157e45894a2441457c2bcc3904e816b1508916f5ef9e5ccc6b24f36637e5a30755fd90f3964907c58109"
    teacher_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OTRkeGhtd3N2NjJzeWxqajZnOHAwcHY3a21lMzh0bDNrcHh0cXk5ZXIwejd1ZzBldnphMCIsImV4cCI6NjE3MDM2ODkyMDB9.EjPXRc18vSyj-zsHGZSMfbfqQFSYduInqBNYISuqhn0"
    
    teacher_email = f"{test_identifier}_teacher@email.com"
    teacher_user = await User.create(
        type="teacher",
        email=teacher_email,
        stake_address=teacher_stake_address,
        active=True,
    )

    supervisor_stake_address = "stake1uxzmzuqz7sx4zejq690jcua8cz6x5ycq9azxnjl9pfw74rcudljz7"
    supervisor_signature = "a40101032720062158204cced8dfc135e686b8a8e397166b3a6800877171f0d4a3275bd93c60a1164377H1+DFJCghAmokzYG84582aa201276761646472657373581de185b17002f40d516640d15f2c73a7c0b46a13002f4469cbe50a5dea8fa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584069919a472deb1b35bbe20efa486d273d1f099a3ffb63b6e30fe1ff7904f293f04f0dbe62ba8bea8c3a875fc7dd1001d465acd3e7a62a6bfe6eb29eaa70237f0a"
    supervisor_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eHptenVxejdzeDR6ZWpxNjkwamN1YThjejZ4NXljcTlhenhuamw5cGZ3NzRyY3VkbGp6NyIsImV4cCI6NjE3MDM2ODkyMDB9.schSQwpz3ZZHlaor5PhZX3MbHQ5TSpu_d1_G4kEMXxg"

    supervisor_email = f"{test_identifier}_supervisor@email.com"
    supervisor_user = await User.create(
        type="supervisor",
        email=supervisor_email,
        stake_address=supervisor_stake_address,
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
        user=teacher_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=student_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=supervisor_user,
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

    created_task = await Task.create(
        identifier=f"{test_identifier}_task_1",
        name=f"{test_name} Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
    )

    # Should be able to reject as teacher, supervisor or organizer

    # Organizer
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/reject",
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_rejected_start": False})
    await created_task.save()

    # Teacher
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/reject",
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_rejected_start": False})
    await created_task.save()

    # Supervisor
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/reject",
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_rejected_start": False})
    await created_task.save()

    # Student - not allowed
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/start/reject",
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_create():
    test_identifier = "test_task_submission_create"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u8d8hlswnwzt33z0v40cywfukvu0vewmmg604fhn34zvdnqmzmx4e"
    signature = "a4010103272006215820c9697a0fad9208c62663b0211c8d7202d83c5943374dc7d0f1ce7de0cb0a6819H1+DFJCghAmokzYG84582aa201276761646472657373581de1da7bfe0e9b84b8c44f655f82393cb338f665dbda34faa6f38d44c6cca166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584006cc5eceae3d439fe59abb9f4a109a783337f4f387cbdb65d119a19474014a4f1fa3ac154d41cdcee7525899d658f3eaacbc2b8012152ad67eb89ebf768b8a07"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OGQ4aGxzd253enQzM3owdjQwY3l3ZnVrdnUwdmV3bW1nNjA0ZmhuMzR6dmRucW16bXg0ZSIsImV4cCI6NjE3MDM2ODkyMDB9.r3r1Uvxmel6OYkQ--faRKHqJRHTdDn1TjKXaaJd1lBU"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
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

    created_task = await Task.create(
        identifier=f"{test_identifier}_task_1",
        name=f"{test_name} Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
        is_approved_start=False
    )

    # Should not be able to make submissions if it is not currently active
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission",
        json={
            "name": f"{test_name} Submission 1",
            "description": ""
        },
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 400

    created_task.update_from_dict({"is_approved_start": True})
    await created_task.save()

    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission",
        json={
            "name": f"{test_name} Submission 1",
            "description": ""
        },
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 200


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_approve():
    test_identifier = "test_task_submission_approve"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u899egcnkhj0samv4fujgq7ss4xkzsdpf6hu6z7k3danfeszt8h7j"
    signature = "a4010103272006215820a3bceed9f5aa3962c8b49fce612b15ab7799e37d7ddfb28f5dda0019ff7623dbH1+DFJCghAmokzYG84582aa201276761646472657373581de1ca5ca313b5e4f8776caa792403d0854d6141a14eafcd0bd68b7b34e6a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840836b30e7c49f743b6b56260a0a45db76c1b0128804982fbb8156a5705d3339ccab90b05697356d568557824c98a84eaf19a92c116b38108d91de3a0c4056be02"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1ODk5ZWdjbmtoajBzYW12NGZ1amdxN3NzNHhrenNkcGY2aHU2ejdrM2RhbmZlc3p0OGg3aiIsImV4cCI6NjE3MDM2ODkyMDB9.VPoLnaNknjp3r5GLavDa0-m1NC_IL5_nm6lKH1yXIvU"
 
    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    student_stake_address = "stake1uxd5n0anqadkyk3378ycdjyacy244ne5an949f8htqlesksram5lz"
    student_signature = "a401010327200621582081ba5a171e618b74e93f736f2d17d63179e3536887500e090a6725d19b89bda3H1+DFJCghAmokzYG84582aa201276761646472657373581de19b49bfb3075b625a31f1c986c89dc1155acf34eccb52a4f7583f985aa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058409fcd21ac6fd0fb8692ab668efe122b6def424f74cdd791cc080dbafb8d8a6d5c0303dbf10a25d523f4e4b856bf56762ec57275f1b0fa0c9922352c56d0e4a10d"
    student_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eGQ1bjBhbnFhZGt5azMzNzh5Y2RqeWFjeTI0NG5lNWFuOTQ5ZjhodHFsZXNrc3JhbTVseiIsImV4cCI6NjE3MDM2ODkyMDB9.rXBruvWss5ftF5kObQ-UhWesOd6CSS2cTL16bv5QXI4"

    student_email = f"{test_identifier}_student@email.com"
    student_user = await User.create(
        type="student",
        email=student_email,
        stake_address=student_stake_address,
        active=True,
    )

    teacher_stake_address = "stake1uxcdyrvvmdnmpx3mduwgfv2uxanxf0achk8ff3rhpv05u0gnuqfhj"
    teacher_signature = "a4010103272006215820e949cb12ef2ceb890f02f594c2e3e0dee5bc361ffe7b91e0cbdc252e949c3ce0H1+DFJCghAmokzYG84582aa201276761646472657373581de1b0d20d8cdb67b09a3b6f1c84b15c376664bfb8bd8e94c4770b1f4e3da166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058401c6203a061b350ef7b5a042eb2b678b88197066b31e8d430965e81e84ef7f9c3dfaa9caeaca0ed311bb38e32ca8fbd362601d0ab4760686d3d6ebd7127a35307"
    teacher_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eGNkeXJ2dm1kbm1weDNtZHV3Z2Z2MnV4YW54ZjBhY2hrOGZmM3JocHYwNXUwZ251cWZoaiIsImV4cCI6NjE3MDM2ODkyMDB9.AOHMYwpTg662liZK_KEQ7_X4f_fAzSKqskQE4VvBSQI"

    teacher_email = f"{test_identifier}_teacher@email.com"
    teacher_user = await User.create(
        type="teacher",
        email=teacher_email,
        stake_address=teacher_stake_address,
        active=True,
    )

    supervisor_stake_address = "stake1u93malsg7fpcqpy5qy33w5duhmgc3qud5wxuj0fwcfvmhsgrzersd"
    supervisor_signature = "a401010327200621582006ef2abd057204350c3b409a857574a6c7fbf9b4964331abad0915e6341e8ceeH1+DFJCghAmokzYG84582aa201276761646472657373581de163befe08f24380049401231751bcbed188838da38dc93d2ec259bbc1a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840df3bffd8aa82ffe4695fe4a32eaa78e030aec653603e9fd0e51f93214c1a0c4251095c1bec4a5c37e385dde179478cc3ce9f5f4fbaffcc72dfded6d94afd9308"
    supervisor_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OTNtYWxzZzdmcGNxcHk1cXkzM3c1ZHVobWdjM3F1ZDV3eHVqMGZ3Y2Z2bWhzZ3J6ZXJzZCIsImV4cCI6NjE3MDM2ODkyMDB9.Y931dKbzvf5nXx4Fd_SiM-dFBt2XRoUGV4rHYGa2R-s"
    
    supervisor_email = f"{test_identifier}_supervisor@email.com"
    supervisor_user = await User.create(
        type="supervisor",
        email=supervisor_email,
        stake_address=supervisor_stake_address,
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
        user=teacher_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=student_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=supervisor_user,
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

    created_task = await Task.create(
        identifier=f"{test_identifier}_task_1",
        name=f"{test_name} Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
        is_approved_start=True
    )

    # Should be able to approve as teacher, supervisor or organizer

    # Organizer
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/approve",
        json={"description": ""},
        headers={"Authorization": "Bearer " + token},
    )
    print(response.json())
    assert response.status_code == 200

    created_task.update_from_dict({"is_approved_completed": False})
    await created_task.save()

    # Teacher
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/approve",
        json={"description": ""},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_approved_completed": False})
    await created_task.save()

    # Supervisor
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/approve",
        json={"description": ""},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_approved_completed": False})
    await created_task.save()

    # Student - not allowed
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/approve",
        json={"description": ""},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_reject():
    test_identifier = "test_task_submission_reject"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u9kgc2gjkxug8nk63p9xtnd85j7mhkrefaesq6u820f7h0g9xytf6"
    signature = "a401010327200621582007b1b76ba4eb9698dfaf65f03abd8166ea6808e6659dace3c2fa33a06f269831H1+DFJCghAmokzYG84582aa201276761646472657373581de16c8c2912b1b883ceda884a65cda7a4bdbbd8794f73006b8753d3ebbda166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584075b9c627eadb288298d3f79f7251314b71c861fdbb7b3584193a6725aa251a546330fd18288abc0b7b96ab09ad52f6268cbefe46dbb9c6539dabc67b44a7bd0c"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OWtnYzJnamt4dWc4bms2M3A5eHRuZDg1ajdtaGtyZWZhZXNxNnU4MjBmN2gwZzl4eXRmNiIsImV4cCI6NjE3MDM2ODkyMDB9.vAHtvfn5bIRelJG-5UTMzg4M2XSPA-Piad40hvq9tQs"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    student_stake_address = "stake1u9qn37zwqdgv3ymncsh2lldhtd8pavyr8l7m6r6l8qtns8g20uk08"
    student_signature = "a4010103272006215820079f06a475ef3b1ce861ef98124915cba648dab964bf5e6d0fbd01fe26f39669H1+DFJCghAmokzYG84582aa201276761646472657373581de14138f84e0350c89373c42eaffdb75b4e1eb0833ffdbd0f5f3817381da166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584088e7c1d298af0cd95a4006d8d133a5fa43333fb39109225a9cd8bbc39e6972e63beb1c82cb1035a07c2647a6fa26b8ee3e16458db1c16979b0a4e8cd8d97b20b"
    student_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OXFuMzd6d3FkZ3YzeW1uY3NoMmxsZGh0ZDhwYXZ5cjhsN202cjZsOHF0bnM4ZzIwdWswOCIsImV4cCI6NjE3MDM2ODkyMDB9.eifiN8MkBTIxQPOJbinKQTwKCNCRKjCADJGv1nEA6Fc"
    
    student_email = f"{test_identifier}_student@email.com"
    student_user = await User.create(
        type="student",
        email=student_email,
        stake_address=student_stake_address,
        active=True,
    )

    teacher_stake_address = "stake1ux8j2sr3qwc43slymf87ny2vumq920ruar0zp9wclhm27kcw5hk26"
    teacher_signature = "a40101032720062158204e10ea30070bb6075e169a6754a8fa8262187b462be777301e78ce885cc0d38eH1+DFJCghAmokzYG84582aa201276761646472657373581de18f25407103b158c3e4da4fe9914ce6c0553c7ce8de2095d8fdf6af5ba166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840ca2ca3cf7cc0bdde2cccb10339e7db19ad044b74a2a384588b6f5a6212389b96af37301df890c6a98524353a92b9b325bc52c247d646da054b0b7209a53e5b0c"
    teacher_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eDhqMnNyM3F3YzQzc2x5bWY4N255MnZ1bXE5MjBydWFyMHpwOXdjbGhtMjdrY3c1aGsyNiIsImV4cCI6NjE3MDM2ODkyMDB9.S4xU8PuVXFaMimx4s3XyueHRRCKjxik9SaL-Y0HQjkY"
    
    teacher_email = f"{test_identifier}_teacher@email.com"
    teacher_user = await User.create(
        type="teacher",
        email=teacher_email,
        stake_address=teacher_stake_address,
        active=True,
    )

    supervisor_stake_address = "stake1uxdgvn69twx9wh8mw68q03kyzn7pglk8vmcn4v4jtt4s8wcfp4nqg"
    supervisor_signature = "a4010103272006215820613103b8d960407b05bd262e95e05a0230bc44d82c785f49d5167c51b9f4e53cH1+DFJCghAmokzYG84582aa201276761646472657373581de19a864f455b8c575cfb768e07c6c414fc147ec766f13ab2b25aeb03bba166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584050cc3e28d30b66322ff0af91be7eb1b6e87733db3c9ba7c98ed1469c44359cc24736a629ca6573ab74b08b474cdfc35dcf48dd9116f5262d95a232220818200f"
    supervisor_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eGRndm42OXR3eDl3aDhtdzY4cTAza3l6bjdwZ2xrOHZtY240djRqdHQ0czh3Y2ZwNG5xZyIsImV4cCI6NjE3MDM2ODkyMDB9.ylDfY9o_bXZjZK53yWJmLrEq1ro5m5_Swt3L5ChKlsk"
    
    supervisor_email = f"{test_identifier}_supervisor@email.com"
    supervisor_user = await User.create(
        type="supervisor",
        email=supervisor_email,
        stake_address=supervisor_stake_address,
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
        user=teacher_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=student_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=supervisor_user,
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

    created_task = await Task.create(
        identifier=f"{test_identifier}_task_1",
        name=f"{test_name} Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
        is_approved_start=True
    )

    # Should be able to approve as teacher, supervisor or organizer

    # Organizer
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/reject",
        json={"description": ""},
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_rejected_completed": False})
    await created_task.save()

    # Teacher
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/reject",
        json={"description": ""},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_rejected_completed": False})
    await created_task.save()

    # Supervisor
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/reject",
        json={"description": ""},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 200

    created_task.update_from_dict({"is_rejected_completed": False})
    await created_task.save()

    # Student - not allowed
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/reject",
        json={"description": ""},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400


@freeze_time("2023-12-27 15:00:00")
async def test_task_submission_review():
    test_identifier = "test_task_submission_review"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uxfjmmek6ae9waae5cdhnxeh4j9smeh9qxeuh6ksgg9tp2gzrkqx6"
    signature = "a4010103272006215820025beda29fed5c6ed765c301dcf5e42bbb8f3b310c5f2e1f60396faa98eb781eH1+DFJCghAmokzYG84582aa201276761646472657373581de1932def36d7725777b9a61b799b37ac8b0de6e501b3cbead0420ab0a9a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584018d7135bb6c38af15283d4eb44248681cb1b825f72fa163fb7111c0def5615338ed1210aa6731ffd62ca9631d00a542c0cc7cb990e352a5164a8e7f324561508"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eGZqbW1lazZhZTl3YWFlNWNkaG54ZWg0ajlzbWVoOXF4ZXVoNmtzZ2c5dHAyZ3pya3F4NiIsImV4cCI6NjE3MDM2ODkyMDB9.tXqE6KFXCebKsa04rBllbdJpcGbC2rVtbTzcAHTo5Pk"
    
    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    student_stake_address = "stake1uyf0uuy04xthwx9geeqncltcug7pqvwhn3sjd5g6vqyrkus2xg4fa"
    student_signature = "a401010327200621582071bd682a6d7d0b76c116b86afe137a5813c6b8cde8099d0600fb2d4d4448a4afH1+DFJCghAmokzYG84582aa201276761646472657373581de112fe708fa9977718a8ce413c7d78e23c1031d79c6126d11a60083b72a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584012f3914329381d5c7324f4291a81750d7e0f4d5f991635b33bc305a69cd73f7da43ffe2e2f14680e581a61f2f3e5923abaf1abdf9671520d461b4f3ab9a2040b"
    student_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eWYwdXV5MDR4dGh3eDlnZWVxbmNsdGN1ZzdwcXZ3aG4zc2pkNWc2dnF5cmt1czJ4ZzRmYSIsImV4cCI6NjE3MDM2ODkyMDB9.QD78iE719lv0zTkVxfji7SXDTTH86y-N3bF-g1GRalU"
    
    student_email = f"{test_identifier}_student@email.com"
    student_user = await User.create(
        type="student",
        email=student_email,
        stake_address=student_stake_address,
        active=True,
    )

    teacher_stake_address = "stake1u8j8lra9pwsr9ks966ttknsde9pz3u78s9c5jdmcxdeewlq6csmjz"
    teacher_signature = "a40101032720062158203608748e6acfb0c635e26c7af9a1535d91104c4723a9792e15d3a2902a809f6eH1+DFJCghAmokzYG84582aa201276761646472657373581de1e47f8fa50ba032da05d696bb4e0dc94228f3c781714937783373977ca166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840b5948a34b047b92072cf18664bca83447653b6df7e6961a9d2ac9692c00dcf15957f21ae70cbbc8598ff927c24c5debef1223f85445a5ae2f4c2f8de56b10d00"
    teacher_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OGo4bHJhOXB3c3I5a3M5NjZ0dGtuc2RlOXB6M3U3OHM5YzVqZG1jeGRlZXdscTZjc21qeiIsImV4cCI6NjE3MDM2ODkyMDB9.vzsN1fcGUz0wKh6Toz0UI0SdyIbnn4PRVQ4RHp3olYk"
    
    teacher_email = f"{test_identifier}_teacher@email.com"
    teacher_user = await User.create(
        type="teacher",
        email=teacher_email,
        stake_address=teacher_stake_address,
        active=True,
    )

    supervisor_stake_address = "stake1u883nd7zpqmj0c3f9rq7wuxnyxe8z4r3jn72ecl66psgp0c570lk0"
    supervisor_signature = "a40101032720062158205421e98c28c04c51dd96706163917c016f40c9b5f9a71cd89f8467ab0a167425H1+DFJCghAmokzYG84582aa201276761646472657373581de1cf19b7c2083727e22928c1e770d321b271547194fcace3fad06080bfa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058409fa4a1b94e5ddb812e4326fb30481456492806ea960e1a0a45b7bffecd1fee667472a688080a979abba4cd9530b81e54a3e70c0a18becc09d1d62d932340560b"
    supervisor_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1ODgzbmQ3enBxbWowYzNmOXJxN3d1eG55eGU4ejRyM2puNzJlY2w2NnBzZ3AwYzU3MGxrMCIsImV4cCI6NjE3MDM2ODkyMDB9.wkgnlKM452LLCV5exVrEpNcg61C6-T3awpJeyw8fJzc"

    supervisor_email = f"{test_identifier}_supervisor@email.com"
    supervisor_user = await User.create(
        type="supervisor",
        email=supervisor_email,
        stake_address=supervisor_stake_address,
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
        user=teacher_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=student_user,
        organization=created_organization,
        area=None,
    )

    await OrganizationMembership.create(
        user=supervisor_user,
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

    created_task = await Task.create(
        identifier=f"{test_identifier}_task_1",
        name=f"{test_name} Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
        is_approved_start=True
    )

    # Organizer
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/review",
        json={"description": "", "extended_deadline": "2024-01-02T00:00:00Z"},
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 200

    task = await Task.filter(identifier=f"{test_identifier}_task_1").first()
    assert task.deadline.timestamp() == datetime.datetime(2024, 1, 2).timestamp()

    # Teacher
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/review",
        json={"description": ""},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 200

    # Supervisor
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/review",
        json={"description": ""},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 200

    # Student - not allowed
    response = client.post(
        f"/organization/{test_identifier}_org_1/task/{test_identifier}_task_1/submission/review",
        json={"description": ""},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400
