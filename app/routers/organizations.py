from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated, List
from tortoise.expressions import Q

from app import dependecy, specs
from app.model import User, UserType, Organization, OrganizationMembership, Task


import logging


logging.basicConfig(
    level=logging.INFO, format="%(filename)s:%(lineno)s %(levelname)s:%(message)s"
)

router = APIRouter(prefix="/organization")


@router.post("/create", response_model=specs.OrganizationSpec)
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


@router.post("/{organization_identifier}/edit", response_model=specs.OrganizationSpec)
async def organization_edit(
    current_user: Annotated[User, Depends(dependecy.get_current_active_user)],
    body: specs.EditOrganizationBodySpec,
    organization_identifier: str,
):
    organization = (
        await Organization.filter(identifier=organization_identifier)
        .prefetch_related("admin")
        .first()
    )
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    if organization.admin != current_user:
        raise HTTPException(
            status_code=400,
            detail=f"User does not have permission to edit organization! Contact {organization.admin.email}!",
        )

    update_dict = {}
    for key, value in body.model_dump().items():
        if value is not None:
            update_dict[key] = value

    await organization.update_from_dict(update_dict)
    await organization.save()

    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


@router.post("/{organization_identifier}/join")
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

    # If is student and organization has at least one area
    # Enforce that student chose an area
    if (
        (current_user.type == UserType.STUDENT.value)
        and (len(organization.areas) > 0)
        and (body.area is None)
    ):
        raise HTTPException(status_code=400, detail="No area selected")

    if (current_user.type != UserType.STUDENT.value) and (body.area is not None):
        raise HTTPException(status_code=400, detail="Only student can select area")

    if body.area is not None and body.area.lower() not in [
        area.lower() for area in organization.areas
    ]:
        raise HTTPException(
            status_code=400, detail="Area selected does not exist in this organization"
        )

    await OrganizationMembership.create(
        user=current_user,
        organization=organization,
        area=None if body.area is None else body.area.lower(),
    )

    return {"message": f"Successfully joined {organization_identifier}"}


@router.get("/{organization_identifier}", response_model=specs.OrganizationSpec)
async def organization_read(organization_identifier: str):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    pydantic_organization = await specs.OrganizationSpec.from_tortoise_orm(organization)

    return pydantic_organization


@router.get("/{organization_identifier}/areas")
async def organization_areas_read(organization_identifier: str):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return organization.areas


@router.get("/{organization_identifier}/tasks", response_model=specs.TasksResponse)
async def organization_tasks_read(
    organization_identifier: str,
    page: Annotated[int, Query(ge=1)] = 1,
    count: Annotated[int, Query(ge=1, le=20)] = 10,
    individual: bool | None = None,
    group: bool | None = None,
):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    if individual is None and group is None:
        individual = True
        group = True
    elif individual is None:
        individual = False
    elif group is None:
        group = False

    tasks: List["Task"] = []

    if individual and group:
        # Page 1 must be from first element to count element
        # Page 2 must be from count element to 2*count element
        tasks = (
            Task.filter(
                Q(group__organization=organization)
                | Q(owner_membership__organization=organization)
            )
            .order_by("-creation_date")
            .offset((page - 1) * count)
            .limit(count)
            .all()
        )
    elif individual:
        tasks = (
            Task.filter(
                Q(owner_membership__organization=organization) & Q(is_individual=True)
            )
            .order_by("-creation_date")
            .offset((page - 1) * count)
            .limit(count)
            .all()
        )
    elif group:
        tasks = (
            Task.filter(Q(group__organization=organization) & Q(is_individual=False))
            .order_by("-creation_date")
            .offset((page - 1) * count)
            .limit(count)
            .all()
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="There are no tasks which are neither group or individual",
        )

    count_tasks = await Task.filter(group__organization=organization).count()
    max_page = (count_tasks // (count + 1)) + 1

    pydantic_tasks = await specs.TaskSpec.from_queryset(tasks)

    return specs.TasksResponse(
        current_page=page, max_page=max_page, tasks=pydantic_tasks
    )


@router.get(
    "/{organization_identifier}/users", response_model=specs.OrganizationUsersResponse
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
