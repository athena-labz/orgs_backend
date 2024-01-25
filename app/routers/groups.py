from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import Q
from typing import Annotated

from app import dependecy, specs
from app.model import User, UserType, OrganizationMembership, Group, GroupMembership
from app.lib import group

import logging


logging.basicConfig(
    level=logging.INFO, format="%(filename)s:%(lineno)s %(levelname)s:%(message)s"
)

router = APIRouter(prefix="/organization/{organization_identifier}/group")


@router.post("/create", response_model=specs.GroupSpec)
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


@router.post("/{group_identifier}/accept")
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


@router.post("/{group_identifier}/reject")
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


@router.post("/{group_identifier}/leave")
async def group_leave(
    group_membership: Annotated[
        GroupMembership, Depends(dependecy.get_current_active_group_membership)
    ]
):
    if group_membership.leader:
        raise HTTPException(status_code=400, detail="Leader cannot leave group")

    await group_membership.update_from_dict({"accepted": False, "rejected": True})
    await group_membership.save()

    return {"message": "Successfully left group"}
