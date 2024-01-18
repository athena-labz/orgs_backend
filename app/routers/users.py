from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.expressions import Q
from typing import Annotated

from app import dependecy, specs
from app.model import User, OrganizationMembership, GroupMembership, Task, UserBalance
from app.lib import cardano, auth, balance, group, environment, utils

import pycardano as pyc
import datetime
import logging


ACCESS_TOKEN_EXPIRE_MINUTES = environment.get("ACCESS_TOKEN_EXPIRE_MINUTES", int)


logging.basicConfig(
    level=logging.INFO, format="%(filename)s:%(lineno)s %(levelname)s:%(message)s"
)

router = APIRouter(prefix="/users")


@router.post("/login", response_model=specs.TokenSpec)
async def user_login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not registered yet",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.stake_address}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=specs.UserSpec)
async def user_register(body: specs.RegisterBodySpec):
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


@router.post("/me/email/confirm")
async def user_email_confirm(
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


@router.post("/me/address/add")
async def user_add_payment_address(
    current_user: Annotated[User, Depends(dependecy.get_current_active_user)],
    body: specs.UserAddPaymentAddressBodySpec,
):
    # Make sure address is valid
    try:
        address = pyc.Address.from_primitive(body.address)

        if address.network != cardano.current_network():
            raise HTTPException(
                status_code=400,
                detail=f"Address is not from current network {str(cardano.current_network())}",
            )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid address")

    await current_user.update_from_dict({"payment_address": body.address})
    await current_user.save()

    return {"message": "Successfully confirmed the email"}


@router.get("/me", response_model=specs.UserSpec)
async def user_read(
    current_user: Annotated[specs.UserSpec, Depends(dependecy.get_current_active_user)]
):
    pydantic_user = await specs.UserSpec.from_tortoise_orm(current_user)

    return pydantic_user


@router.get("/me/organizations", response_model=specs.UserOrganizationsResponse)
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


@router.get(
    "/me/organization/{organization_identifier}/tasks",
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


@router.get(
    "/me/organization/{organization_identifier}/balance",
    response_model=specs.BalanceResponse,
)
async def user_balance_read(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ]
):
    owed_balance = await balance.get_user_owed_balance(current_membership)
    escrowed_balance = await balance.get_user_escrowed_balance(current_membership)
    claimed_balance = await balance.get_user_claimed_balance(current_membership)

    last_claim_date = (
        await UserBalance.filter(Q(user_member=current_membership) & Q(is_claimed=True))
        .order_by("-claim_date")
        .first()
    )

    if last_claim_date is not None:
        last_claim_date = last_claim_date.claim_date.isoformat()

    return specs.BalanceResponse(
        owed=owed_balance,
        available=owed_balance - escrowed_balance,
        escrowed=escrowed_balance,
        claimed=claimed_balance,
        last_claim_date=last_claim_date,
    )


@router.get(
    "/me/organization/{organization_identifier}/groups",
    response_model=specs.OrganizationGroupsResponse,
)
async def user_groups_read(
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
