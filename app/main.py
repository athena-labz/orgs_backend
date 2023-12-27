from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from tortoise.contrib.fastapi import register_tortoise
from tortoise.expressions import Q

from app.model import (
    User,
    UserType,
    Organization,
    OrganizationMembership,
    OrganizationType,
    Group,
    GroupMembership,
    Task,
    TaskReward,
    TaskAction,
)

from app.lib import cardano, auth, environment, utils, group

import dependecy
import specs

import pycardano as pyc
import datetime
import logging


ACCESS_TOKEN_EXPIRE_MINUTES = environment.get("ACCESS_TOKEN_EXPIRE_MINUTES", int)
DATABASE = environment.get("DATABASE")


logging.basicConfig(
    level=logging.INFO, format="%(filename)s:%(lineno)s %(levelname)s:%(message)s"
)


# https://fastapi.tiangolo.com
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {}


@app.post("/token", response_model=specs.TokenSpec)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.stake_address}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=specs.UserSpec)
async def user_read(
    current_user: Annotated[specs.UserSpec, Depends(dependecy.get_current_active_user)]
):
    pydantic_user = await specs.UserSpec.from_tortoise_orm(current_user)
    return pydantic_user


@app.get("/users/me/organizations", response_model=specs.UserOrganizationsResponse)
async def user_organizations_read(
    current_user: Annotated[specs.UserSpec, Depends(dependecy.get_current_active_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    count: Annotated[int, Query(ge=1, le=20)] = 10,
):
    organization_memberships = await (
        OrganizationMembership.filter(user=current_user)
        .order_by("-membership_date")
        .offset((page - 1) * count)
        .limit(count)
        .prefetch_related("organization")
        .all()
    )

    count_users = await OrganizationMembership.filter(user=current_user).count()
    max_page = (count_users // (count + 1)) + 1

    pydantic_organizations = []
    for membership in organization_memberships:
        pydantic_organizations.append(
            await specs.OrganizationSpec.from_tortoise_orm(membership.organization)
        )

    return specs.UserOrganizationsResponse(
        current_page=page, max_page=max_page, organizations=pydantic_organizations
    )


@app.post("/users/register", response_model=specs.UserSpec)
async def register(body: specs.RegisterBodySpec):
    try:
        address = pyc.Address.from_primitive(body.stake_address)
    except Exception as e:
        logging.error(f"Error while trying to convert stake address {e}")
        raise HTTPException(status_code=400, detail="Invalid stake address format")

    if address.network != pyc.Network.MAINNET:
        raise HTTPException(
            status_code=400,
            detail="Stake address is from preprod, but it must be from mainnet",
        )

    if not cardano.verify_signature(body.signature, body.stake_address):
        raise HTTPException(status_code=400, detail="Invalid signature")

    user = await User.filter(
        Q(stake_address=body.stake_address) | Q(email=body.email)
    ).first()
    if user is not None:
        raise HTTPException(status_code=400, detail="Stake address or email taken")

    user = await User.create(
        type=body.user_type.value, email=body.email, stake_address=body.stake_address
    )
    pydantic_user = await specs.UserSpec.from_tortoise_orm(user)

    return pydantic_user


@app.post("/users/confirm/email")
async def confirm_email(
    email_validation_string: str,
    current_user: Annotated[User, Depends(dependecy.get_current_user)],
):
    if current_user.active:
        raise HTTPException(status_code=400, detail="Email already verified")

    if email_validation_string != current_user.email_validation_string:
        await current_user.update_from_dict(
            {"email_validation_string": utils.string_generator()}
        )
        await current_user.save()

        raise HTTPException(status_code=400, detail="Wrong email string")

    await current_user.update_from_dict({"active": True})
    await current_user.save()

    return {"message": "Successfully confirmed the email"}


@app.post("/organization/create", response_model=specs.OrganizationSpec)
async def organization_create(
    current_user: Annotated[User, Depends(dependecy.get_current_active_user)],
    body: specs.CreateOrganizationBodySpec,
):
    if not current_user.type == UserType.ORGANIZER.value:
        raise HTTPException(status_code=400, detail="User not of type organizer")

    existing_organization = await Organization.filter(
        identifier=body.identifier
    ).first()
    if existing_organization is not None:
        raise HTTPException(status_code=400, detail="Organization identifier taken")

    organization = await Organization.create(
        identifier=body.identifier,
        type=body.organization_type.value,
        name=body.name,
        description=body.description,
        students_password=body.students_password,
        teachers_password=body.teachers_password,
        supervisor_password=body.supervisor_password,
        areas=[area.lower() for area in body.areas],
        admin=current_user,
    )

    await OrganizationMembership.create(user=current_user, organization=organization)

    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


@app.get(
    "/organization/{organization_identifier}", response_model=specs.OrganizationSpec
)
async def organization_read(organization_identifier: str):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


@app.get("/organization/{organization_identifier}/areas")
async def organization_areas_read(organization_identifier: str):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return organization.areas


@app.get(
    "/organization/{organization_identifier}/tasks",
    response_model=specs.TasksResponse,
)
async def organization_tasks_read(
    organization_identifier: str,
    page: Annotated[int, Query(ge=1)] = 1,
    count: Annotated[int, Query(ge=1, le=20)] = 10,
):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Page 1 must be from first element to count element
    # Page 2 must be from count element to 2*count element
    tasks = (
        Task.filter(group__organization=organization)
        .order_by("-creation_date")
        .offset((page - 1) * count)
        .limit(count)
        .all()
    )

    count_tasks = await Task.filter(group__organization=organization).count()
    max_page = (count_tasks // (count + 1)) + 1

    pydantic_tasks = await specs.TaskSpec.from_queryset(tasks)

    return specs.TasksResponse(
        current_page=page, max_page=max_page, tasks=pydantic_tasks
    )


@app.post(
    "/organization/{organization_identifier}/edit",
    response_model=specs.OrganizationSpec,
)
async def organization_edit(
    current_user: Annotated[User, Depends(dependecy.get_current_active_user)],
    body: specs.EditOrganizationBodySpec,
    organization_identifier: str,
):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    if organization.admin != current_user:
        raise HTTPException(
            status_code=400, detail="User does not have permission to edit organization"
        )

    update_dict = {}
    for key, value in body.model_dump().items():
        if value is not None:
            update_dict[key] = value

    await organization.update_from_dict(update_dict)
    await organization.save()

    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


@app.post("/organization/{organization_identifier}/join")
async def organization_join(
    current_user: Annotated[User, Depends(dependecy.get_current_active_user)],
    body: specs.JoinOrganizationBodySpec,
    organization_identifier: str,
):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    # If user has already joined organization, return 400
    existing_membership = await OrganizationMembership.filter(
        organization=organization, user=current_user
    ).first()
    if existing_membership is not None:
        raise HTTPException(
            status_code=400, detail="User is already part of this organization"
        )

    if current_user.type == UserType.STUDENT.value:
        if body.password != organization.students_password:
            raise HTTPException(status_code=400, detail="Wrong student password")
    elif current_user.type == UserType.TEACHER.value:
        if body.password != organization.teachers_password:
            raise HTTPException(status_code=400, detail="Wrong teacher password")
    elif current_user.type == UserType.SUPERVISOR.value:
        if body.password != organization.supervisor_password:
            raise HTTPException(status_code=400, detail="Wrong supervisor password")
    else:
        raise HTTPException(
            status_code=400, detail="Organizer cannot join any organizations"
        )

    if body.area is not None and body.area.lower() not in organization.areas:
        raise HTTPException(
            status_code=400, detail="Area selected does not exist in this organization"
        )

    await OrganizationMembership.create(
        user=current_user,
        organization=organization,
        area=None if body.area is None else body.area.lower(),
    )

    return {"message": f"Successfully joined {organization_identifier}"}


@app.get(
    "/organization/{organization_identifier}/users",
    response_model=specs.OrganizationUsersResponse,
)
async def organization_users_read(
    organization_identifier: str,
    page: Annotated[int, Query(ge=1)] = 1,
    count: Annotated[int, Query(ge=1, le=20)] = 10,
):
    organization_memberships = await (
        OrganizationMembership.filter(organization__identifier=organization_identifier)
        .order_by("-membership_date")
        .offset((page - 1) * count)
        .limit(count)
        .prefetch_related("user")
        .all()
    )

    count_users = await OrganizationMembership.filter(
        organization__identifier=organization_identifier
    ).count()
    max_page = (count_users // (count + 1)) + 1

    pydantic_users = []
    for membership in organization_memberships:
        pydantic_users.append(await specs.UserSpec.from_tortoise_orm(membership.user))

    return specs.OrganizationUsersResponse(
        current_page=page, max_page=max_page, users=pydantic_users
    )


@app.get(
    "/users/me/organization/{organization_identifier}/groups",
    response_model=specs.OrganizationGroupsResponse,
)
async def organization_groups_read(
    organization_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    count: Annotated[int, Query(ge=1, le=20)] = 10,
):
    group_memberships = await (
        GroupMembership.filter(user=organization_membership.user)
        .order_by("-invite_date")
        .offset((page - 1) * count)
        .limit(count)
        .prefetch_related("group")
        .all()
    )

    count_groups = await OrganizationMembership.filter(
        user=organization_membership.user
    ).count()
    max_page = (count_groups // (count + 1)) + 1

    pydantic_groups_membership = []
    for membership in group_memberships:
        group_membership = await specs.GroupMembershipSpec.from_tortoise_orm(membership)

        pydantic_groups_membership.append(
            specs.GroupMembershipExtendedSpec(
                **group_membership.model_dump(), group=membership.group
            )
        )

    return specs.OrganizationGroupsResponse(
        current_page=page, max_page=max_page, groups=pydantic_groups_membership
    )


@app.post(
    "/organization/{organization_identifier}/group/create",
    response_model=specs.GroupSpec,
)
async def group_create(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    body: specs.CreateGroupBodySpec,
):
    user = current_membership.user
    organization = current_membership.organization

    if not user.type == UserType.STUDENT.value:
        # Only students can create groups
        raise HTTPException(status_code=400, detail="User not of type student")

    if organization.type != OrganizationType.GROUPS.value:
        # Only organization of type groups can have manually created groups
        raise HTTPException(status_code=400, detail="Organization not of type groups")

    if await group.is_member_of_group(current_membership):
        raise HTTPException(
            status_code=400, detail="Student is already member of a group"
        )

    # If there is a group with the same identifier, return error
    existing_group = await Group.filter(
        Q(identifier=body.identifier) & Q(organization=organization)
    ).first()
    if existing_group is not None:
        raise HTTPException(status_code=400, detail="Group identifier taken")

    members = []  # This is so we don't change the database until everything is okay
    for member_email in body.members:
        member_user = await User.filter(email=member_email).first()
        if member_user is None:
            raise HTTPException(
                status_code=400, detail="Group participant account not found"
            )

        if member_user.type != UserType.STUDENT.value:
            raise HTTPException(
                status_code=400, detail="Group participant is not student"
            )

        membership = (
            await OrganizationMembership.filter(
                Q(user=member_user) & Q(organization=organization)
            )
            .prefetch_related("user", "organization")
            .first()
        )
        if membership is None:
            raise HTTPException(
                status_code=400,
                detail="Group participant is not a member of this organization",
            )

        if membership.area != current_membership.area:
            raise HTTPException(
                status_code=400,
                detail="Group participant has different area than leader",
            )

        if await group.is_member_of_group(membership):
            raise HTTPException(
                status_code=400,
                detail="Group participant is already member of a group",
            )

        members.append(member_user)

    created_group = await Group.create(
        identifier=body.identifier, name=body.name, organization=organization
    )

    await GroupMembership.create(
        group=created_group,
        user=user,
        accepted=True,
        leader=True,
    )

    for member_user in members:
        await GroupMembership.create(group=created_group, user=member_user)

    pydantic_group = await specs.GroupSpec.from_tortoise_orm(created_group)

    return pydantic_group


@app.post("/organization/{organization_identifier}/group/{group_identifier}/accept")
async def group_accept(
    group_membership: Annotated[
        GroupMembership, Depends(dependecy.get_current_group_membership)
    ]
):
    if group_membership.accepted is True:
        raise HTTPException(status_code=400, detail="User is already member of group")

    if group_membership.rejected is True:
        raise HTTPException(status_code=400, detail="User has already rejected invite")

    await group_membership.update_from_dict({"accepted": True})
    await group_membership.save()

    return {"message": "Successfully accepted group invite"}


@app.post("/organization/{organization_identifier}/group/{group_identifier}/reject")
async def group_reject(
    group_membership: Annotated[
        GroupMembership, Depends(dependecy.get_current_group_membership)
    ]
):
    if group_membership.accepted is True:
        raise HTTPException(status_code=400, detail="User is already member of group")

    if group_membership.rejected is True:
        raise HTTPException(status_code=400, detail="User has already rejected invite")

    await group_membership.update_from_dict({"rejected": True})
    await group_membership.save()

    return {"message": "Successfully rejected group invite"}


@app.post("/organization/{organization_identifier}/group/leave")
async def group_leave(
    group_membership: Annotated[
        GroupMembership, Depends(dependecy.get_current_active_group_membership)
    ]
):
    await group_membership.update_from_dict({"accepted": False, "rejected": True})
    await group_membership.save()

    return {"message": "Successfully left group"}


@app.post(
    "/organization/{organization_identifier}/group/task/create",
    response_model=specs.TaskSpec,
)
async def group_task_create(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    group_membership: Annotated[
        GroupMembership, Depends(dependecy.get_current_active_group_membership)
    ],
    body: specs.CreateTaskBodySpec,
):
    # Make sure there is no other task with this identifier in this
    # organization
    existing_task = await Task.filter(
        Q(identifier=body.identifier)
        & Q(group__organization=current_membership.organization)
    ).first()
    if existing_task is not None:
        raise HTTPException(status_code=400, detail="Task identifier taken")

    # Get group members
    group_members = (
        await GroupMembership.filter(Q(group=group_membership.group) & Q(accepted=True))
        .prefetch_related("user")
        .all()
    )

    # Map group members to email
    rewards = {}
    for member in group_members:
        if not member.user.email in body.rewards:
            raise HTTPException(
                status_code=400,
                detail=f"User {member.user.email} was left without rewards",
            )

        rewards[member.user.email] = (body.rewards[member.user.email], member)

    for email in body.rewards.keys():
        if not email in rewards:
            raise HTTPException(
                status_code=400,
                detail="Select reward for user not member of this group",
            )

    task = await Task.create(
        identifier=body.identifier,
        name=body.name,
        description=body.description,
        deadline=body.deadline,
        group=group_membership.group,
    )

    for reward, member in rewards.values():
        await TaskReward.create(group_member=member, task=task, reward=reward)

    pydantic_task = await specs.TaskSpec.from_tortoise_orm(task)

    return pydantic_task


@app.get(
    "/organization/{organization_identifier}/task/{task_identifier}",
    response_model=specs.TaskSpec,
)
async def task_read(task: Annotated[Task, Depends(dependecy.get_task)]):
    pydantic_task = await specs.TaskSpec.from_tortoise_orm(task)

    return pydantic_task


@app.get(
    "/organization/{organization_identifier}/task/{task_identifier}/members",
    response_model=list[specs.UserSpec],
)
async def task_members_read(task: Annotated[Task, Depends(dependecy.get_task)]):
    members = (
        await GroupMembership.filter(Q(group=task.group) & Q(accepted=True))
        .prefetch_related("user")
        .all()
    )

    users = []
    for member in members:
        users.append(await specs.UserSpec.from_tortoise_orm(member.user))

    return users


@app.get(
    "/organization/{organization_identifier}/task/{task_identifier}/actions",
    response_model=specs.TaskActionsResponse,
)
async def task_actions_read(
    task: Annotated[Task, Depends(dependecy.get_task)],
    page: Annotated[int, Query(ge=1)] = 1,
    count: Annotated[int, Query(ge=1, le=20)] = 10,
):
    task_actions = (
        TaskAction.filter(task=task)
        .order_by("-action_date")
        .offset((page - 1) * count)
        .limit(count)
        .all()
    )

    count_tasks = await TaskAction.filter(task=task).count()
    max_page = (count_tasks // (count + 1)) + 1

    pydantic_actions = await specs.TaskActionSpec.from_queryset(task_actions)

    return specs.TaskActionsResponse(
        current_page=page, max_page=max_page, actions=pydantic_actions
    )


@app.post(
    "/organization/{organization_identifier}/task/{task_identifier}/start/approve"
)
async def task_start_approve(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
):
    if not auth.has_review_privileges(current_membership.user):
        raise HTTPException(
            status_code=400, detail="Only teacher can approve task start"
        )

    if task.is_approved_start or task.is_rejected_start:
        raise HTTPException(status_code=400, detail="Task has already started")

    task.update_from_dict({"is_approved_start": True, "is_rejected_start": False})
    task_action = TaskAction(
        name="Approve task start",
        description="",
        author=current_membership.user,
        task=task,
    )

    await task.save()
    await task_action.save()

    return {"message": "Successfully aproved start of task"}


@app.post("/organization/{organization_identifier}/task/{task_identifier}/start/reject")
async def task_start_reject(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
):
    if not auth.has_review_privileges(current_membership.user):
        raise HTTPException(
            status_code=400, detail="Does not have permission to approve task start"
        )

    if task.is_approved_start or task.is_rejected_start:
        raise HTTPException(status_code=400, detail="Task has already started")

    task.update_from_dict({"is_approved_start": False, "is_rejected_start": True})
    task_action = TaskAction(
        name="Reject task start",
        description="",
        author=current_membership.user,
        task=task,
    )

    await task.save()
    await task_action.save()

    return {"message": "Successfully rejected start of task"}


@app.post("/organization/{organization_identifier}/task/{task_identifier}/submission")
async def task_submission(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
    body: specs.SubmitTaskBodySpec,
):
    # Make sure user is part of task
    if not await group.is_member_of_specific_group(current_membership, task.group):
        raise HTTPException(status_code=400, detail="User is not part of this task")

    if not task.is_approved_start:
        raise HTTPException(
            status_code=400, detail="Task has not been approved by a teacher yet"
        )

    if task.is_rejected_completed or task.is_approved_completed:
        raise HTTPException(status_code=400, detail="Task is not active anymore")

    task_action = TaskAction(
        name=body.name,
        description=body.description,
        author=current_membership.user,
        task=task,
        is_submission=True,
    )

    await task_action.save()

    return {"message": "Successfully submitted task for review"}


@app.post(
    "/organization/{organization_identifier}/task/{task_identifier}/submission/approve"
)
async def task_submission_approve(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
    body: specs.RejectTaskBodySpec,
):
    if not auth.has_review_privileges(current_membership.user):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to approve task submission",
        )

    if not task.is_approved_start:
        raise HTTPException(
            status_code=400, detail="Task has not been approved by a teacher yet"
        )

    if task.is_rejected_completed or task.is_approved_completed:
        raise HTTPException(status_code=400, detail="Task is not active anymore")

    task.update_from_dict(
        {"is_approved_completed": True, "is_rejected_completed": False}
    )
    task_action = TaskAction(
        name="Approve task submission",
        description=body.description,
        author=current_membership.user,
        task=task,
        is_review=True,
    )

    await task.save()
    await task_action.save()

    return {"message": "Successfully approved task submission"}


@app.post(
    "/organization/{organization_identifier}/task/{task_identifier}/submission/reject"
)
async def task_submission_reject(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
    body: specs.RejectTaskBodySpec,
):
    if not auth.has_review_privileges(current_membership.user):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to reject task submission",
        )

    if not task.is_approved_start:
        raise HTTPException(
            status_code=400, detail="Task has not been approved by a teacher yet"
        )

    if task.is_rejected_completed or task.is_approved_completed:
        raise HTTPException(status_code=400, detail="Task is not active anymore")

    task.update_from_dict(
        {"is_approved_completed": False, "is_rejected_completed": True}
    )
    task_action = TaskAction(
        name="Reject task submission",
        description=body.description,
        author=current_membership.user,
        task=task,
        is_review=True,
    )

    await task.save()
    await task_action.save()

    return {"message": "Successfully rejected task submission"}


@app.post(
    "/organization/{organization_identifier}/task/{task_identifier}/submission/review"
)
async def task_submission_review(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
    body: specs.ReviewTaskBodySpec,
):
    if not auth.has_review_privileges(current_membership.user):
        raise HTTPException(
            status_code=400,
            detail="User does not have permission to review task submission",
        )

    if not task.is_approved_start:
        raise HTTPException(
            status_code=400, detail="Task has not been approved by a teacher yet"
        )

    if task.is_rejected_completed or task.is_approved_completed:
        raise HTTPException(status_code=400, detail="Task is not active anymore")

    if body.extended_deadline is not None:
        task.update_from_dict({"deadline": body.extended_deadline})
        await task.save()

    task_action = TaskAction(
        name="Asked to review and resubmit task",
        description=body.description,
        author=current_membership.user,
        task=task,
        is_review=True,
    )

    await task_action.save()

    return {"message": "Successfully asked for a task resubmission"}


@app.get(
    "/users/me/organization/{organization_identifier}/tasks",
    response_model=specs.TasksResponse,
)
async def user_tasks_read(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    count: Annotated[int, Query(ge=1, le=20)] = 10,
):
    group_membership = await group.get_user_group_membership(current_membership)
    if group_membership is None:
        return specs.TasksResponse(current_page=1, max_page=1, tasks=[])

    await group_membership.fetch_related("group")

    # Page 1 must be from first element to count element
    # Page 2 must be from count element to 2*count element
    tasks = (
        Task.filter(group=group_membership.group)
        .order_by("-creation_date")
        .offset((page - 1) * count)
        .limit(count)
        .all()
    )

    count_tasks = await Task.filter(group=group_membership.group).count()
    max_page = (count_tasks // (count + 1)) + 1

    pydantic_tasks = await specs.TaskSpec.from_queryset(tasks)

    return specs.TasksResponse(
        current_page=page, max_page=max_page, tasks=pydantic_tasks
    )


register_tortoise(app, db_url=DATABASE, modules={"models": ["model"]})
