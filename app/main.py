from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from tortoise.contrib.fastapi import register_tortoise
from tortoise.expressions import Q

from model import (
    User,
    UserType,
    Organization,
    OrganizationMembership,
    OrganizationType,
    Group,
    GroupMembership,
)
from lib import cardano, auth, environment, utils, group

import dependecy
import specs

import pycardano as pyc
import datetime


ACCESS_TOKEN_EXPIRE_MINUTES = environment.get("ACCESS_TOKEN_EXPIRE_MINUTES", int)
DATABASE = environment.get("DATABASE")


# https://fastapi.tiangolo.com
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
app = FastAPI()


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


@app.get("/users/me/", response_model=specs.UserSpec)
async def read_users_me(
    current_user: Annotated[specs.UserSpec, Depends(dependecy.get_current_active_user)]
):
    pydantic_user = await specs.UserSpec.from_tortoise_orm(current_user)
    return pydantic_user


@app.post("/users/register", response_model=specs.UserSpec)
async def register(body: specs.RegisterBodySpec):
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
        print(email_validation_string, current_user.email_validation_string)
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
        areas=body.areas,
        admin=current_user,
    )
    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


@app.get(
    "/organization/{organization_identifier}", response_model=specs.OrganizationSpec
)
async def organization_view(organization_identifier: str):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


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

    if current_user.type == UserType.STUDENT.value:
        if body.password != organization.students_password:
            raise HTTPException(status_code=400, detail="Wrong student password")
    elif current_user.type == UserType.TEACHER.value:
        if body.password != organization.teachers_password:
            raise HTTPException(status_code=400, detail="Wrong teacher password")
    else:
        raise HTTPException(
            status_code=400, detail="Organizer cannot join any organizations"
        )

    await OrganizationMembership.create(user=current_user, organization=organization)

    return {"message": f"Successfully joined {organization_identifier}"}


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
    for member_email, reward in body.members.items():
        member_user = await User.filter(email=member_email).first()
        if member_user is None:
            raise HTTPException(
                status_code=400, detail="Group participant account not found"
            )

        membership = await OrganizationMembership.filter(
            Q(user=member_user) & Q(organization=organization)
        ).prefetch_related("user", "organization").first()
        if membership is None:
            raise HTTPException(
                status_code=400,
                detail="Group participant is not a member of this organization",
            )

        if await group.is_member_of_group(membership):
            raise HTTPException(
                status_code=400,
                detail="Group participant is already member of a group",
            )

        members.append((member_user, reward))

    created_group = await Group.create(
        identifier=body.identifier, name=body.name, organization=organization
    )

    await GroupMembership.create(
        group=created_group,
        user=user,
        reward_tokens=body.leader_reward,
        accepted=True,
        leader=True,
    )

    for member_user, reward in members:
        await GroupMembership.create(
            group=created_group, user=member_user, reward_tokens=reward
        )

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


@app.post("/organization/{organization_identifier}/group/{group_identifier}/leave")
async def group_leave(
    group_membership: Annotated[
        GroupMembership, Depends(dependecy.get_current_active_group_membership)
    ]
):
    await group_membership.update_from_dict({"accepted": False, "rejected": True})
    await group_membership.save()

    return {"message": "Successfully left group"}


register_tortoise(app, db_url=DATABASE, modules={"models": ["model"]})
