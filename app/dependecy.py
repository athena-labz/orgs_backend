from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from tortoise.query_utils import Prefetch
from tortoise.expressions import Q

from jose import jwt, JWTError

from app.lib import environment
from app.model import (
    User,
    Organization,
    OrganizationMembership,
    Group,
    GroupMembership,
    Task,
)
import specs


ALGORITHM = environment.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = environment.get("ACCESS_TOKEN_EXPIRE_MINUTES", int)
SECRET_KEY = environment.get("SECRET_KEY")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = specs.TokenDataSpec(username=username)
    except JWTError as e:
        raise credentials_exception

    user = await User.filter(stake_address=token_data.username).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


async def get_current_user_membership(
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_identifier: str,
):
    organization = await Organization.filter(identifier=organization_identifier).first()
    if organization is None:
        raise HTTPException(status_code=400, detail="Organization does not exist")

    organization_membership = await OrganizationMembership.filter(
        Q(user=current_user) & Q(organization=organization)
    ).first()

    if organization_membership is None:
        raise HTTPException(
            status_code=400, detail="User is not member of this organization"
        )

    await organization_membership.fetch_related("user")
    await organization_membership.fetch_related("organization")

    return organization_membership


async def get_current_group_membership(
    current_membership: Annotated[
        OrganizationMembership, Depends(get_current_user_membership)
    ],
    group_identifier: str,
):
    group = await Group.filter(
        Q(identifier=group_identifier) & Q(organization=current_membership.organization)
    ).first()
    if group is None:
        raise HTTPException(status_code=400, detail="Group does not exist")

    group_membership = (
        await GroupMembership.filter(Q(user=current_membership.user) & Q(group=group))
        .prefetch_related("group")
        .first()
    )
    if group_membership is None:
        raise HTTPException(
            status_code=400, detail="User has no membership with this group"
        )

    return group_membership


async def get_current_active_group_membership(
    current_membership: Annotated[
        OrganizationMembership, Depends(get_current_user_membership)
    ]
):
    group_membership = (
        await GroupMembership.filter(
            Q(user=current_membership.user)
            & Q(group__organization=current_membership.organization)
            & Q(accepted=True)
        )
        .prefetch_related("group")
        .first()
    )
    if group_membership is None:
        raise HTTPException(
            status_code=400,
            detail="User has no active membership with this organization",
        )

    return group_membership


async def get_task(organization_identifier: str, task_identifier: str):
    task = (
        await Task.filter(
            Q(identifier=task_identifier)
            & Q(
                Q(owner_membership__organization__identifier=organization_identifier)
                | Q(group__organization__identifier=organization_identifier)
            )
        )
        .prefetch_related("owner_membership", "group")
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


async def get_individual_task(organization_identifier: str, task_identifier: str):
    task = (
        await Task.filter(
            Q(identifier=task_identifier)
            & Q(owner_membership__organization__identifier=organization_identifier)
            & Q(is_individual=True)
        )
        .prefetch_related("owner_membership")
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


async def get_group_task(organization_identifier: str, task_identifier: str):
    task = (
        await Task.filter(
            Q(identifier=task_identifier)
            & Q(group__organization__identifier=organization_identifier)
            & Q(is_individual=False)
        )
        .prefetch_related("group")
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
