from app.model import User, UserBalance, Organization, OrganizationMembership, TaskFund

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
        Q(user_member=user_membership) & Q(is_escrowed=True) & Q(is_claimed=False)
    ).all()

    escrowed_balance = 0
    for balance in escrowed_balances:
        escrowed_balance += balance.amount

    return escrowed_balance


async def get_user_claimed_balance(
    user_membership: OrganizationMembership,
) -> int:
    claimed_balances = await UserBalance.filter(
        Q(user_member=user_membership) & Q(is_claimed=True) & Q(is_escrowed=False)
    ).all()

    claimed_balance = 0
    for balance in claimed_balances:
        claimed_balance += balance.amount

    return claimed_balance


async def collect_amount(
    user_membership: OrganizationMembership, amount: int
) -> Tuple[List["UserBalance"], int]:
    owed_balances = (
        await UserBalance.filter(
            Q(user_member=user_membership) & Q(is_claimed=False) & Q(is_escrowed=False)
        )
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


async def claim_balance(balance: UserBalance):
    balance.is_claimed = True
    balance.claim_date = datetime.datetime.utcnow()
    await balance.save()


async def escrow_balance(balance: UserBalance, task_fund: TaskFund):
    balance.is_escrowed = True
    balance.escrow_task_fund = task_fund
    
    await balance.save()


async def release_balance(balance: UserBalance):
    await balance.fetch_related("user_member")
    await balance.fetch_related("escrow_task_fund")
    await balance.escrow_task_fund.fetch_related("task")
    await balance.escrow_task_fund.task.fetch_related("owner_membership")

    balance.user_member = balance.escrow_task_fund.task.owner_membership
    balance.is_escrowed = False
    balance.escrow_task_fund = None

    await balance.save()


async def retreat_balance(balance: UserBalance):
    await balance.fetch_related("escrow_task_fund")
    await balance.escrow_task_fund.fetch_related("user_member")

    balance.user_member = balance.escrow_task_fund.user_member
    balance.is_escrowed = False
    balance.escrow_task_fund = None

    await balance.save()


async def fund_escrow(task_fund: TaskFund):
    consumed_balances, change_amount = await collect_amount(
        task_fund.user_member, task_fund.amount
    )

    if change_amount == 0:
        for balance in consumed_balances:
            await escrow_balance(balance, task_fund)

        return

    for balance in consumed_balances:
        await claim_balance(balance)

    await UserBalance.create(amount=change_amount, user_member=task_fund.user_member)
    await UserBalance.create(
        amount=task_fund.amount,
        user_member=task_fund.user_member,
        is_escrowed=True,
        escrow_task_fund=task_fund,
    )


async def fund_release(task_fund: TaskFund):
    balances: List["UserBalance"] = await UserBalance.filter(
        Q(escrow_task_fund=task_fund) & Q(is_claimed=False) & Q(is_escrowed=True)
    ).all()
    if len(balances) == 0:
        raise ValueError(f"User fund has no balance escrowed")

    for balance in balances:
        await release_balance(balance)


async def fund_retreat(task_fund: TaskFund):
    balances: List["UserBalance"] = await UserBalance.filter(
        Q(escrow_task_fund=task_fund) & Q(is_claimed=False) & Q(is_escrowed=True)
    ).all()
    if len(balances) == 0:
        raise ValueError(f"User fund has no balance escrowed")

    for balance in balances:
        await retreat_balance(balance)


async def send_amount(
    sender: OrganizationMembership,
    receiver: OrganizationMembership,
    balances: List["UserBalance"],
    amount: int,
):
    sum_balance = 0
    for balance in balances:
        balance.is_claimed = True
        balance.claim_date = datetime.datetime.utcnow()

        sum_balance += balance.amount

        await balance.save()

    if (sum_balance - amount) < 0:
        raise ValueError("Tried to send amount with less balance than it could")

    await UserBalance.create(amount=amount, is_claimed=False, user_member=sender)

    if (sum_balance - amount) > 0:
        await UserBalance.create(
            amount=sum_balance - amount, is_claimed=False, user_member=receiver
        )


async def make_payment(
    sender_membership: OrganizationMembership,
    receiver_membership: OrganizationMembership,
    amount: int,
):
    consumed_balances, change_amount = await collect_amount(sender_membership, amount)

    await send_amount(
        sender_membership, receiver_membership, consumed_balances, change_amount
    )
