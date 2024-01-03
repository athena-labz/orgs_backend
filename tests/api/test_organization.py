from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.main import app
from app.model import (
    Organization,
    OrganizationMembership,
    Group,
    GroupMembership,
    Task,
    User,
)

import datetime


@freeze_time("2023-12-27 15:00:00")
async def test_organization_create():
    test_identifier = "test_organization_create"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u86eef32xaw9wmgl47ghe5glmkpcpdp4hhnen9re0t3wryclfqeug"
    signature = "a40101032720062158203588d4d71ecebc0d8ed8fac2e1149b0eed95c531b6adec91cc53ae712873c747H1+DFJCghAmokzYG84582aa201276761646472657373581de1f59ca62a375c576d1faf917cd11fdd8380b435bde79994797ae2e193a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058405f5c128c6c2eac8ed7c6cc3eef58084b7637b539a00f9e0cebec83cd17fa75fb20d55cdf396d8a4b2a25820d05b189e3d376b88e36fb405eea7c37c5f7755605"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1ODZlZWYzMnhhdzl3bWdsNDdnaGU1Z2xta3BjcGRwNGhobmVuOXJlMHQzd3J5Y2xmcWV1ZyIsImV4cCI6NjE3MDM2ODkyMDB9.RMsHypEipXOlGTco69Ct6YnwlU17GcFoUMwPbves2Qo"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    response = client.post(
        "/organization/create",
        json={
            "identifier": f"{test_identifier}_org_1",
            "name": f"{test_name} Org 1",
            "description": "",
            "students_password": "pass123",
            "teachers_password": "pass123",
            "supervisor_password": "pass123",
            "areas": [],
        },
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200

    # Make sure organization was created
    org_created = await Organization.filter(
        identifier=f"{test_identifier}_org_1"
    ).first()
    assert org_created is not None


@freeze_time("2023-12-27 15:00:00")
async def test_organization_edit():
    test_identifier = "test_organization_edit"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u9sxyvsnjplq263u8ma5nm92k5jeefljxkudmjjt48y7gegye857s"
    signature = "a401010327200621582069b280db5138604da16ddc2e2d3a2318997bfa10cbe0cde3878af6115fbadc7eH1+DFJCghAmokzYG84582aa201276761646472657373581de160623213907e056a3c3efb49ecaab5259ca7f235b8ddca4ba9c9e465a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584046d3aa2e92e45c260daf6bec6f3831f6f609959772140081f0684ed1e7e3e77f3ba1e25128a8e05021c4b24223c812994ed17b2063875f25577cffbfda773303"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OXN4eXZzbmpwbHEyNjN1OG1hNW5tOTJrNWplZWZsanhrdWRtamp0NDh5N2dlZ3llODU3cyIsImV4cCI6NjE3MDM2ODkyMDB9.Q5-hPMkvMALZHg_jYkJZypKNqjgeif76Up84zn0JoKg"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    wrong_stake_address = "stake1u806xqj6xe6wvgdjlkgxpgxq5zmcwqhavx42r2c2snmfu3qy3klgl"
    wrong_signature = "a40101032720062158200f1de50aec05b77dd410bf5573d0ff71d300631cedcef9a451fcb1d568bb2c24H1+DFJCghAmokzYG84582aa201276761646472657373581de1dfa3025a3674e621b2fd9060a0c0a0b78702fd61aaa1ab0a84f69e44a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840c090df8430abb1d986f0ecfc090b4da34845d8173ffbb813f2db04b231d5a37b8f5f6fb1e995f534550743808ea7c9c680a02546cefafa8d121c5b46d4db1808"
    wrong_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1ODA2eHFqNnhlNnd2Z2RqbGtneHBneHE1em1jd3FoYXZ4NDJyMmMyc25tZnUzcXkza2xnbCIsImV4cCI6NjE3MDM2ODkyMDB9.8xQKsudBX7qeMG0vb5ojsFV7NZUZCDo6i1rqaZKWbcY"

    wrong_email = "wrong_user@email.com"
    wrong_user = await User.create(
        type="organizer",
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

    response = client.post(
        f"/organization/{test_identifier}_org_1/edit",
        json={"name": f"{test_name} Org 2"},
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200

    # Make sure organization was created
    org_created = await Organization.filter(id=created_organization.id).first()

    assert org_created is not None
    assert org_created.name == f"{test_name} Org 2"

    # Try to edit again
    response = client.post(
        f"/organization/{test_identifier}_org_1/edit",
        json={"name": f"{test_name} Org 1"},
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200

    # Make sure organization was created
    org_created = await Organization.filter(id=created_organization.id).first()

    assert org_created is not None
    assert org_created.name == f"{test_name} Org 1"

    # Try with user who is not admin
    response = client.post(
        f"/organization/{test_identifier}_org_1/edit",
        json={"name": f"{test_name} Org 2"},
        headers={"Authorization": "Bearer " + wrong_token},
    )

    assert response.status_code == 400


@freeze_time("2023-12-27 15:00:00")
async def test_organization_read():
    test_identifier = "test_organization_read"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u9f08xnxar0vg9nq8an4w7hpc9cju2yp94gwfv0aaxdtpnqvss6qd"
    signature = "a4010103272006215820fad317e10ce4b33eb175935675b0e3ce37d81aa1ddd670dcb696cf5c3f14f4daH1+DFJCghAmokzYG84582aa201276761646472657373581de152f39a66e8dec416603f67577ae1c1712e28812d50e4b1fde99ab0cca166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058408885e35931065cee6d51adabe17ea8c7f7f8789b8887de4434d97c3bec0a666584b2ea2b99c3fe91d13043a30798654cec10b82e8992c33fb6b412064f559003"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OWYwOHhueGFyMHZnOW5xOGFuNHc3aHBjOWNqdTJ5cDk0Z3dmdjBhYXhkdHBucXZzczZxZCIsImV4cCI6NjE3MDM2ODkyMDB9.JLp7w3-GjDQvrbpYWSxV13awcnZVXIqXFA-he4yl3A8"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    await Organization.create(
        identifier=f"{test_identifier}_org_1",
        name=f"{test_name} Org 1",
        description="",
        students_password="pass123",
        teachers_password="pass123",
        supervisor_password="pass123",
        areas=[],
        admin=created_user,
    )

    response = client.get(
        f"/organization/{test_identifier}_org_1",
        headers={"Authorization": "Bearer " + token},
    )

    assert response.status_code == 200
    assert (
        response.json().items()
        >= {
            "identifier": "test_organization_read_org_1",
            "name": "Test Organization Read Org 1",
            "description": "",
            "supervisor_password": "pass123",
            "areas": [],
        }.items()
    )


@freeze_time("2023-12-27 15:00:00")
async def test_organization_join():
    test_identifier = "test_organization_join"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    organizer_stake_address = (
        "stake1uyk5sc2xpek3sas4xy26fsdq8j25p29ndvr9hrjmnvt68qqn3ynzw"
    )
    organizer_signature = "a4010103272006215820e483cd9db7f10e84a45ec86ecdfdf79ee65cc434ac39998221bd8f478459daddH1+DFJCghAmokzYG84582aa201276761646472657373581de12d4861460e6d1876153115a4c1a03c9540a8b36b065b8e5b9b17a380a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840117cc91a191fe3fbce4f528fff0fc0045c317617862906ed473ee3e7ceeba2443ceb58097a9b604494758813cd9eed64724e79bc628f8184a76a8b174e39d50c"
    organizer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eWs1c2MyeHBlazNzYXM0eHkyNmZzZHE4ajI1cDI5bmR2cjlocmptbnZ0NjhxcW4zeW56dyIsImV4cCI6NjE3MDM2ODkyMDB9.I7-e5vJrVHhpyxu3heh7Q9aIcA2BEwGR8av_rc8aMXw"

    organizer_email = f"{test_identifier}_organizer@email.com"
    created_organizer = await User.create(
        type="organizer",
        email=organizer_email,
        stake_address=organizer_stake_address,
        active=True,
    )

    student_stake_address = (
        "stake1ux4hhcj6ymqytjjxveh9d4zr272l8p6fsvcjnu4guma28jqemp4u5"
    )
    student_signature = "a40101032720062158205d98aa05e36343d3f1a5d21f36a1dbcaeb3c75187eef765505f932a99ee7feb1H1+DFJCghAmokzYG84582aa201276761646472657373581de1ab7be25a26c045ca46666e56d4435795f38749833129f2a8e6faa3c8a166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584037f630e11eeca3e4a554616fb5bc80ee1c298fb92e85fea2adcf29d63e95dac443d7dd8d8afaed027e52acf1374f87fe30cb2f779686a216f1dd781f026bf409"
    student_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eDRoaGNqNnltcXl0amp4dmVoOWQ0enIyNzJsOHA2ZnN2Y2pudTRndW1hMjhqcWVtcDR1NSIsImV4cCI6NjE3MDM2ODkyMDB9.e1Sl9yoTqsA65_0-csIzVHH47MNuBz9Hm0rISjErJ4E"

    student_email = f"{test_identifier}_student@email.com"
    created_student = await User.create(
        type="student",
        email=student_email,
        stake_address=student_stake_address,
        active=True,
    )

    teacher_stake_address = (
        "stake1uy9h69dln8dc7gzxytjm4a2ene2hhshm0lwdr3cus8a98mgwszpwd"
    )
    teacher_signature = "a40101032720062158207dd7292ce6806bb7d9ca60cc330e3cdd7868b7fb9dd5a9311bb8f5cc407f0124H1+DFJCghAmokzYG84582aa201276761646472657373581de10b7d15bf99db8f204622e5baf5599e557bc2fb7fdcd1c71c81fa53eda166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058409ecf344690d95b538067ddddb35578f146ec21dee7a443246fa0297d745e3e0c8e7fdcf20a9ffd19ad08c19a5b12bbf906e25ebb0d171d5f618034a0fd083c00"
    teacher_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eTloNjlkbG44ZGM3Z3p4eXRqbTRhMmVuZTJoaHNobTBsd2RyM2N1czhhOThtZ3dzenB3ZCIsImV4cCI6NjE3MDM2ODkyMDB9.uVHhOl1ZgOhIcg4lFxmgRRRb2tJPH-A9fIJ05oyXzCE"

    teacher_email = f"{test_identifier}_teacher@email.com"
    created_teacher = await User.create(
        type="teacher",
        email=teacher_email,
        stake_address=teacher_stake_address,
        active=True,
    )

    supervisor_stake_address = (
        "stake1u95uwety0ugsja9tgpc5kzva2zhgaxs884kdgk44jff4lnc0p7wf6"
    )
    supervisor_signature = "a4010103272006215820260c180f50047ce1c0454f895e804ae256b54ad69d4021eb43d53c38f7e829e9H1+DFJCghAmokzYG84582aa201276761646472657373581de169c765647f110974ab40714b099d50ae8e9a073d6cd45ab592535fcfa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d3137303336383932303058405711bd72641ca2e2cdeadaf9a4a8b6e961d5d2a0bf51d89560d7fcc6069d300d7a306b3c9be11360ff9ff39cadfa6164ed6b859573febc0ab8ae7cde6c4b6800"
    supervisor_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OTV1d2V0eTB1Z3NqYTl0Z3BjNWt6dmEyemhnYXhzODg0a2RnazQ0amZmNGxuYzBwN3dmNiIsImV4cCI6NjE3MDM2ODkyMDB9.o0tu_KMVgelDKO87oJYclhL2Jdl9Nr87A9GlNWbvE-k"

    supervisor_email = f"{test_identifier}_supervisor@email.com"
    created_supervisor = await User.create(
        type="supervisor",
        email=supervisor_email,
        stake_address=supervisor_stake_address,
        active=True,
    )

    created_organization = await Organization.create(
        identifier=f"{test_identifier}_org_1",
        name=f"{test_name} Org 1",
        description="",
        students_password="student123",
        teachers_password="teacher123",
        supervisor_password="supervisor123",
        areas=["Math"],
        admin=created_organizer,
    )

    # =========== Student ===========
    # Make all important tests with the student

    # Assume that if the tests work with the student, it
    # works with the other roles

    # Then check that the other roles cannot join using
    # the password of others

    # Try joining with wrong password
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"wrong", "area": "Math"},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400

    # Try joining with area that does not exist
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"student123", "area": "Meth"},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400

    # Try joining with no area as a student
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"student123"},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400

    # Join with teacher password
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"teacher123", "area": "Math"},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400

    # Join with supervisor password
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"supervisor123", "area": "Math"},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400

    # Actually join - successfull
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"student123", "area": "Math"},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 200

    # Join after already in organization
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"student123", "area": "Math"},
        headers={"Authorization": "Bearer " + student_token},
    )
    assert response.status_code == 400

    # Make sure organization membership was created
    membership = await OrganizationMembership.filter(
        user=created_student, organization=created_organization
    ).first()
    assert membership is not None
    assert membership.area == "math"

    # =========== Teacher ===========

    # Try to join with area as a teacher
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": "teacher123", "area": "Math"},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 400

    # Join with student password
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"student123"},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 400

    # Join with supervisor password
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"supervisor123"},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"teacher123"},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 200

    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"teacher123"},
        headers={"Authorization": "Bearer " + teacher_token},
    )
    assert response.status_code == 400

    # =========== Supervisor ===========

    # Try to join with area as a supervisor
    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": "supervisor123", "area": "Math"},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"student123"},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"teacher123"},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 400

    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"supervisor123"},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 200

    response = client.post(
        f"/organization/{test_identifier}_org_1/join",
        json={"password": f"supervisor123"},
        headers={"Authorization": "Bearer " + supervisor_token},
    )
    assert response.status_code == 400


@freeze_time("2023-12-27 15:00:00")
async def test_organization_areas_read():
    test_identifier = "test_organization_areas_read"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uy9var3jqsjekv9pttafgthpyha00h5rynge3fgyr8tsmmcn5f7jf"
    signature = "a401010327200621582060d3aaa732a14a137bc6186c357c99dcf7fe0ef613ca95a2125e00409e055397H1+DFJCghAmokzYG84582aa201276761646472657373581de10ace8e3204259b30a15afa942ee125faf7de8324d198a50419d70defa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d313730333638393230305840860ae983a3940441d0bac852dc7ff4f1a58a4427ea41014b157f57efb32012d1e78d93e15dcd543bce128f2f995f6fd7f173f40c9270e8964f5ccf860361ae02"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eTl2YXIzanFzamVrdjlwdHRhZmd0aHB5aGEwMGg1cnluZ2UzZmd5cjh0c21tY241ZjdqZiIsImV4cCI6NjE3MDM2ODkyMDB9.WAcHXGe6Gk-6MbUxu4tcRG8ZXdhfhQh8X7cfy58-akA"

    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    await Organization.create(
        identifier=f"{test_identifier}_org_1",
        name=f"{test_name} Org 1",
        description="",
        students_password="pass123",
        teachers_password="pass123",
        supervisor_password="pass123",
        areas=["Math", "science", "HISTORY"],
        admin=created_user,
    )

    response = client.get(f"/organization/{test_identifier}_org_1/areas")

    assert response.status_code == 200
    assert response.json() == ["Math", "science", "HISTORY"]


@freeze_time("2023-12-27 15:00:00")
async def test_organization_tasks_read():
    test_identifier = "test_organization_tasks_read"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uyrkzfxrettuefnwjghcc92m7ech4ygy0djcj9uv2w78tnga5pln2"
    signature = "a40101032720062158207d62bc4f321b56bc86ac8ac7dd16efbf99638c8baa6482ef2f93d60f00e03b5cH1+DFJCghAmokzYG84582aa201276761646472657373581de1076124c3cad7cca66e922f8c155bf6717a91047b6589178c53bc75cda166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584074c1e6879bb1f6298eae9db6ed62cd64e364e0aa7d6f98c7565520ff20859aeac18635997c65806558b3eeb15593f96df2d7c6219b1a81afdfcd654b259ef704"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1eXJremZ4cmV0dHVlZm53amdoY2M5Mm03ZWNoNHlneTBkamNqOXV2Mnc3OHRuZ2E1cGxuMiIsImV4cCI6NjE3MDM2ODkyMDB9.74_dx3-5_kL6kohLRAosa5ErZ5B0tZz3pjBiFBo8NYQ"

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
    )

    await Task.create(
        identifier=f"{test_identifier}_task_1",
        name=f"{test_name} Task 1",
        description="",
        deadline=datetime.datetime(2024, 1, 1),
        group=created_group,
    )

    response = client.get(f"/organization/{test_identifier}_org_1/tasks")

    assert response.status_code == 200

    assert response.json()["current_page"] == 1
    assert response.json()["max_page"] == 1

    assert isinstance(response.json()["tasks"], list)
    assert len(response.json()["tasks"]) == 1

    assert (
        response.json()["tasks"][0].items()
        >= {
            "identifier": "test_organization_tasks_read_task_1",
            "name": "Test Organization Tasks Read Task 1",
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
async def test_organization_users_read():
    test_identifier = "test_organization_users_read"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1uxqhn4jyp9neusxezxu5lz4f9yn3ps47y2ad86pz6wvzwhs0hlujc"
    email = f"{test_identifier}@email.com"
    created_user = await User.create(
        type="organizer",
        email=email,
        stake_address=stake_address,
        active=True,
    )

    other_stake_address = "stake1u8cyqc3m4tctxyxrctnth5jar0mf4gg8pmw0wv3fwz026wgcgrjxd"
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
        areas=["Math"],
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
        area="math",
    )

    response = client.get(f"/organization/{test_identifier}_org_1/users")
    assert response.status_code == 200

    assert response.json()["current_page"] == 1
    assert response.json()["max_page"] == 1

    assert isinstance(response.json()["users"], list)
    assert len(response.json()["users"]) == 2

    assert (
        response.json()["users"][0].items()
        >= {
            "type": "student",
            "email": "test_organization_users_read_other@email.com",
            "stake_address": "stake1u8cyqc3m4tctxyxrctnth5jar0mf4gg8pmw0wv3fwz026wgcgrjxd",
            "active": True,
        }.items()
    )

    assert (
        response.json()["users"][1].items()
        >= {
            "type": "organizer",
            "email": "test_organization_users_read@email.com",
            "stake_address": "stake1uxqhn4jyp9neusxezxu5lz4f9yn3ps47y2ad86pz6wvzwhs0hlujc",
            "active": True,
        }.items()
    )


@freeze_time("2023-12-27 15:00:00")
async def test_organization_groups_read():
    test_identifier = "test_organization_groups_read"
    test_name = " ".join([word.capitalize() for word in test_identifier.split("_")])

    client = TestClient(app)

    stake_address = "stake1u8r7ytuwpg0rrdqwawhq4f6c2zmqkt7c6qsng6ppsfswh7sdz4gku"
    signature = "a401010327200621582024c4a3f381475aa6a25d1d64f24966b68d3e705f74a54f09dab58921fe2ebe9cH1+DFJCghAmokzYG84582aa201276761646472657373581de1c7e22f8e0a1e31b40eebae0aa75850b60b2fd8d0213468218260ebfaa166686173686564f458403d3d3d3d3d3d4f4e4c59205349474e20494620594f552041524520494e206170702e617468656e616c61626f2e636f6d3d3d3d3d3d3d31373033363839323030584074ade694d0a9339eb8e9ee738e7a578fbbc7dea22f4b54e1581e090bb4c5173c52507f6020025d5117814974096866ced6a57b2e0463292f0cad63c6960ba908"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFrZTF1OHI3eXR1d3BnMHJyZHF3YXdocTRmNmMyem1xa3Q3YzZxc25nNnBwc2Zzd2g3c2R6NGdrdSIsImV4cCI6NjE3MDM2ODkyMDB9.cJ0cLSGs5S8tiXm9f15k7KZxgQYHRvJiMXL4t4DHkVc"

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

    other_organization = await Organization.create(
        identifier=f"{test_identifier}_org_2",
        name=f"{test_name} Org 2",
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

    created_group_1 = await Group.create(
        identifier=f"{test_identifier}_group_1",
        name=f"{test_name} Group 1",
        organization=created_organization,
    )

    await GroupMembership.create(
        group=created_group_1,
        user=created_user,
        accepted=True,
        leader=True,
        invite_date=datetime.datetime(2024, 1, 1)
    )

    created_group_2 = await Group.create(
        identifier=f"{test_identifier}_group_2",
        name=f"{test_name} Group 2",
        organization=created_organization,
    )

    await GroupMembership.create(
        group=created_group_2,
        user=created_user,
        accepted=True,
        leader=True,
        invite_date=datetime.datetime(2024, 1, 1)
    )

    created_group_3 = await Group.create(
        identifier=f"{test_identifier}_group_3",
        name=f"{test_name} Group 3",
        organization=other_organization,
    )

    response = client.get(
        f"/users/me/organization/{test_identifier}_org_1/groups",
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 200

    assert response.json()["current_page"] == 1
    assert response.json()["max_page"] == 1

    assert isinstance(response.json()["groups"], list)
    assert len(response.json()["groups"]) == 2

    assert (
        response.json()["groups"][0].items()
        >= {
            "leader": True,
            "accepted": True,
            "rejected": False,
            "invite_date": "2024-01-01T00:00:00Z",
        }.items()
    )

    assert "group" in response.json()["groups"][0]
    assert response.json()["groups"][0]["group"].items() >= {
        "identifier": "test_organization_groups_read_group_1",
        "name": "Test Organization Groups Read Group 1",
    }.items()

    assert (
        response.json()["groups"][1].items()
        >= {
            "leader": True,
            "accepted": True,
            "rejected": False,
            "invite_date": "2024-01-01T00:00:00Z",
        }.items()
    )

    assert "group" in response.json()["groups"][1]
    assert response.json()["groups"][1]["group"].items() >= {
        "identifier": "test_organization_groups_read_group_2",
        "name": "Test Organization Groups Read Group 2",
    }.items()
