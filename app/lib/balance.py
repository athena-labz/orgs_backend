from app.model import User, UserBalance, Organization, OrganizationMembership

from tortoise.expressions import Q
from typing import Tuple, List

import datetime


async def get_user_owed_balance(
    user_membership: OrganizationMembership,
) -> int:
    owed_balances = await UserBalance.filter(
        Q(user_member=user_membership) & Q(is_claimed=False)
    ).all()

    owed_balance = 0
    for balance in owed_balances:
        owed_balance += balance.amount

    return owed_balance


async def get_user_available_balance(
    user_membership: OrganizationMembership,
) -> int:
    available_balances = await UserBalance.filter(
        Q(user_member=user_membership) & Q(is_escrowed=False) & Q(is_claimed=False)
    ).all()

    available_balance = 0
    for balance in available_balances:
        available_balance += balance.amount

    return available_balance


async def get_user_escrowed_balance(
    user_membership: OrganizationMembership,
) -> int:
    escrowed_balances = await UserBalance.filter(
        Q(user_member=user_membership) & Q(is_escrowed=True)
    ).all()

    escrowed_balance = 0
    for balance in escrowed_balances:
        escrowed_balance += balance.amount

    return escrowed_balance


async def get_user_claimed_balance(
    user_membership: OrganizationMembership,
) -> int:
    claimed_balances = await UserBalance.filter(
        Q(user_member=user_membership) & Q(is_claimed=True)
    ).all()

    claimed_balance = 0
    for balance in claimed_balances:
        claimed_balance += balance.amount

    return claimed_balance


async def collect_amount(
    user_membership: OrganizationMembership, amount: int
) -> Tuple[List["UserBalance"], int]:
    owed_balances = (
        await UserBalance.filter(Q(user_member=user_membership) & Q(is_claimed=False))
        .order_by("amount")
        .all()
    )

    collected: List["UserBalance"] = []
    total_balance = 0
    for balance in owed_balances:
        collected.append(balance)
        total_balance += balance.amount

        if total_balance >= amount:
            break

    return (collected, total_balance - amount)


async def make_payment(
    sender_membership: OrganizationMembership,
    receiver_membership: OrganizationMembership,
    amount: int,
):
    consumed_balances, change_amount = await collect_amount(sender_membership, amount)

    for balance in consumed_balances:
        balance.is_claimed = True
        balance.claim_date = datetime.datetime.utcnow()

        await balance.save()

    await UserBalance.create(
        amount=change_amount, is_claimed=False, user_member=sender_membership
    )

    await UserBalance.create(
        amount=amount, is_claimed=False, user_member=receiver_membership
    )
