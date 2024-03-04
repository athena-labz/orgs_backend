from fastapi import APIRouter, HTTPException, Depends, Query
from tortoise.expressions import Q
from typing import Annotated

from app import dependecy, specs
from app.lib import balance, auth, group
from app.model import (
    UserBalance,
    OrganizationMembership,
    GroupMembership,
    Task,
    TaskFund,
    TaskReward,
    TaskAction,
)


import logging


logging.basicConfig(
    level=logging.INFO, format="%(filename)s:%(lineno)s %(levelname)s:%(message)s"
)

router = APIRouter(prefix="/organization/{organization_identifier}/task")


@router.post("/create/group", response_model=specs.TaskSpec)
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
        is_individual=False,
    )

    for reward, member in rewards.values():
        await TaskReward.create(group_member=member, task=task, reward=reward)

    pydantic_task = await specs.TaskSpec.from_tortoise_orm(task)

    return pydantic_task


@router.post("/create", response_model=specs.TaskSpec)
async def individual_task_create(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    body: specs.CreateIndividualTaskBodySpec,
):
    # Make sure there is no other task with this identifier in this
    # organization
    existing_task = await Task.filter(
        Q(identifier=body.identifier)
        & Q(group__organization=current_membership.organization)
    ).first()
    if existing_task is not None:
        raise HTTPException(status_code=400, detail="Task identifier taken")

    task = await Task.create(
        identifier=body.identifier,
        name=body.name,
        description=body.description,
        deadline=body.deadline,
        is_individual=True,
        owner_membership=current_membership,
    )

    pydantic_task = await specs.TaskSpec.from_tortoise_orm(task)

    return pydantic_task


@router.post("/{task_identifier}/start/approve")
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


@router.post("/{task_identifier}/start/reject")
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


@router.post("/{task_identifier}/submission")
async def task_submission(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
    body: specs.SubmitTaskBodySpec,
):
    if not await auth.has_task_user_privileges(current_membership, task):
        raise HTTPException(
            status_code=400, detail="User does not have user permissions for this task"
        )

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


@router.post("/{task_identifier}/submission/approve")
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

    if task.is_individual:
        funds = await TaskFund.filter(task=task).all()

        if not task.owner_membership:
            raise ValueError(f"Task {task.identifier} is individual but has no owner")

        for fund in funds:
            await fund.fetch_related("user_member")
            await fund.fetch_related("task")

            await balance.fund_release(fund)

            fund.is_completed = True
            await fund.save()
    else:
        rewards = await TaskReward.filter(task=task).all()

        for reward in rewards:
            await reward.fetch_related("group_member")
            await reward.group_member.fetch_related("user")
            await reward.group_member.fetch_related("group")
            await reward.group_member.group.fetch_related("organization")

            # Find user organization membership
            user_membership = await OrganizationMembership.filter(
                Q(user=reward.group_member.user)
                & Q(organization=reward.group_member.group.organization)
            ).first()
            if user_membership is None:
                raise ValueError(
                    f"Could not find user membership for group membership {reward.group_member.id}"
                )

            reward.is_completed = True
            await reward.save()

            await UserBalance.create(amount=reward.reward, user_member=user_membership)

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


@router.post("/{task_identifier}/submission/reject")
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

    if task.is_individual:
        funds = await TaskFund.filter(task=task).all()

        if not task.owner_membership:
            raise ValueError(f"Task {task.identifier} is individual but has no owner")

        for fund in funds:
            await fund.fetch_related("user_member")
            await fund.fetch_related("task")

            await balance.fund_retreat(fund)

            fund.is_completed = True
            await fund.save()
    else:
        rewards = await TaskReward.filter(task=task).all()

        for reward in rewards:
            reward.is_completed = True
            await reward.save()

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


@router.post("/{task_identifier}/submission/review")
async def task_submission_review(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_task)],
    body: specs.ReviewTaskBodySpec,
):
    if not await auth.has_task_user_privileges(current_membership, task):
        raise HTTPException(
            status_code=400, detail="User does not have user permissions for this task"
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


@router.post("/{task_identifier}/fund")
async def task_fund(
    current_membership: Annotated[
        OrganizationMembership, Depends(dependecy.get_current_user_membership)
    ],
    task: Annotated[Task, Depends(dependecy.get_individual_task)],
    body: specs.FundTaskBodySpec,
):
    if not task.is_approved_start:
        raise HTTPException(
            status_code=400, detail="Task has not been approved by a teacher yet"
        )

    if task.is_rejected_completed or task.is_approved_completed:
        raise HTTPException(status_code=400, detail="Task is not active anymore")

    if task.is_individual == False:
        raise HTTPException(status_code=400, detail="Task must be individual to fund")

    if current_membership.area is not None:
        if current_membership.area == task.owner_membership.area:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot fund task from student of same school. {current_membership.area}",
            )

    # Make sure user has balance
    user_balance = await balance.get_user_available_balance(current_membership)
    if user_balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"User does not have enough balance. Has {user_balance} tokens in wallet.",
        )

    # Check if there exists a task fund from this user to this task already
    existing_task_fund = await TaskFund.filter(
        Q(user_member=current_membership) & Q(task=task)
    ).first()
    if existing_task_fund is not None:
        raise HTTPException(
            status_code=400, detail=f"User has already funded this task"
        )

    task_fund = await TaskFund.create(
        amount=body.amount, user_member=current_membership, task=task
    )

    await balance.fund_escrow(task_fund)

    task_action = TaskAction(
        name="Task funded",
        description=f"Task funded with {body.amount} tokens. Funds will be available upon completion.",
        author=current_membership.user,
        task=task,
    )
    await task_action.save()

    return {"message": "Successfully funded task"}


@router.get("/{task_identifier}", response_model=specs.TaskSpec)
async def task_read(task: Annotated[Task, Depends(dependecy.get_task)]):
    pydantic_task = await specs.TaskSpec.from_tortoise_orm(task)

    return pydantic_task


@router.get("/{task_identifier}/members", response_model=list[specs.UserSpec])
async def task_members_read(task: Annotated[Task, Depends(dependecy.get_group_task)]):
    members = (
        await GroupMembership.filter(Q(group=task.group) & Q(accepted=True))
        .prefetch_related("user")
        .all()
    )

    users = []
    for member in members:
        users.append(await specs.UserSpec.from_tortoise_orm(member.user))

    return users


@router.get("/{task_identifier}/owner", response_model=specs.UserSpec)
async def task_owner_read(
    task: Annotated[Task, Depends(dependecy.get_individual_task)]
):
    await task.fetch_related("owner_membership")
    await task.owner_membership.fetch_related("user")

    pydantic_user = await specs.UserSpec.from_tortoise_orm(task.owner_membership.user)
    return pydantic_user


@router.get("/{task_identifier}/actions", response_model=specs.TaskActionsResponse)
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
