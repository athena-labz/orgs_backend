from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from app.lib import utils

from enum import Enum

import datetime


# Register
class UserType(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ORGANIZER = "organizer"
    SUPERVISOR = "supervisor"


class User(models.Model):
    id = fields.IntField(pk=True)

    type = fields.CharField(max_length=16)
    email = fields.CharField(max_length=128, unique=True, index=True)
    stake_address = fields.CharField(max_length=128, unique=True, index=True)
    token = fields.CharField(max_length=256, null=True)

    payment_address = fields.CharField(max_length=128, unique=False, null=True)

    # If the current user is active / verified
    # active = fields.BooleanField(default=False)
    active = fields.BooleanField(default=True)
    email_validation_string = fields.CharField(
        max_length=128, default=utils.string_generator
    )

    register_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id", "token", "email_validation_string"]


UserSpec = pydantic_model_creator(User, name="User")


class Organization(models.Model):
    id = fields.IntField(pk=True)
    identifier = fields.CharField(max_length=64, unique=True, index=True)

    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=512)

    students_password = fields.CharField(max_length=32)
    teachers_password = fields.CharField(max_length=32)
    supervisor_password = fields.CharField(max_length=32)

    areas = fields.JSONField()  # should be array of string

    admin: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        model_name="models.User", related_name="created_organizations"
    )

    creation_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id", "students_password", "teachers_password"]


OrganizationSpec = pydantic_model_creator(Organization, name="Organization")


class OrganizationMembership(models.Model):
    id = fields.IntField(pk=True)

    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        model_name="models.User", related_name="membership_organizations", index=True
    )
    organization: fields.ForeignKeyRelation[Organization] = fields.ForeignKeyField(
        model_name="models.Organization", related_name="membership_users", index=True
    )

    # Area the student selected for this organization
    area = fields.CharField(max_length=64, null=True)

    membership_date = fields.DatetimeField(default=datetime.datetime.utcnow)


class Group(models.Model):
    id = fields.IntField(pk=True)

    # Is unique to the organization
    identifier = fields.CharField(max_length=64, index=True)
    organization: fields.ForeignKeyRelation["Organization"] = fields.ForeignKeyField(
        model_name="models.Organization", related_name="created_groups", index=True
    )

    # Tasks from orgs of type GROUP will always create a new group
    # for each task based on the selected members
    source = fields.CharField(max_length=32, default="user_created")
    name = fields.CharField(max_length=128)

    creation_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id", "source"]


GroupSpec = pydantic_model_creator(Group, name="Group")


class GroupMembership(models.Model):
    id = fields.IntField(pk=True)

    group: fields.ForeignKeyRelation["Group"] = fields.ForeignKeyField(
        model_name="models.Group", related_name="memberhip_users"
    )
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        model_name="models.User", related_name="membership_groups"
    )

    leader = fields.BooleanField(default=False)
    accepted = fields.BooleanField(default=False)
    rejected = fields.BooleanField(default=False)

    invite_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id"]


GroupMembershipSpec = pydantic_model_creator(GroupMembership, name="GroupMembership")


class Task(models.Model):
    id = fields.IntField(pk=True)

    identifier = fields.CharField(
        max_length=64, index=True
    )  # Unique in the organization

    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=1024)
    deadline = fields.DatetimeField()

    is_individual = fields.BooleanField(default=False)

    # Only if it is not individual
    group: fields.ForeignKeyRelation["Group"] = fields.ForeignKeyField(
        model_name="models.Group", related_name="group_tasks", index=True, null=True
    )  # Participants of the task

    # Only if it is individual
    owner_membership: fields.ForeignKeyRelation[
        "OrganizationMembership"
    ] = fields.ForeignKeyField(
        model_name="models.OrganizationMembership",
        related_name="individual_tasks",
        index=True,
        null=True,
    )

    is_approved_start = fields.BooleanField(default=False)  # By teacher
    is_rejected_start = fields.BooleanField(default=False)

    is_approved_completed = fields.BooleanField(default=False)  # By teacher
    is_rejected_completed = fields.BooleanField(default=False)

    is_rewards_claimed = fields.BooleanField(default=False)

    creation_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id"]


TaskSpec = pydantic_model_creator(Task, name="Task")


class TaskReward(models.Model):
    id = fields.IntField(pk=True)

    reward = fields.BigIntField()
    is_completed = fields.BooleanField(default=False)

    group_member: fields.ForeignKeyRelation["GroupMembership"] = fields.ForeignKeyField(
        model_name="models.GroupMembership", related_name="task_rewards"
    )
    task: fields.ForeignKeyRelation["Task"] = fields.ForeignKeyField(
        model_name="models.Task", related_name="rewards"
    )

    complete_date = fields.DatetimeField(null=True)


class TaskFund(models.Model):
    id = fields.IntField(pk=True)

    amount = fields.BigIntField()
    is_completed = fields.BooleanField(default=False)

    user_member: fields.ForeignKeyRelation[
        "OrganizationMembership"
    ] = fields.ForeignKeyField(
        model_name="models.OrganizationMembership", related_name="task_funds"
    )
    task: fields.ForeignKeyRelation["Task"] = fields.ForeignKeyField(
        model_name="models.Task", related_name="funds"
    )

    complete_date = fields.DatetimeField(null=True)


class TaskAction(models.Model):
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=1024)

    author: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        model_name="models.User", related_name="actions"
    )  # Who is doing this action?
    task: fields.ForeignKeyRelation["Task"] = fields.ForeignKeyField(
        model_name="models.Task", related_name="actions"
    )  # Which task does this refer to?

    is_submission = fields.BooleanField(default=False)
    is_review = fields.BooleanField(default=False)

    action_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id"]


TaskActionSpec = pydantic_model_creator(TaskAction, name="TaskAction")


class UserBalance(models.Model):
    id = fields.IntField(pk=True)

    # The amount of tokens which is owed to a user
    amount = fields.BigIntField()

    is_claimed = fields.BooleanField(default=False)

    is_escrowed = fields.BooleanField(default=False)
    escrow_task_fund: fields.ForeignKeyRelation["TaskFund"] = fields.ForeignKeyField(
        model_name="models.TaskFund", related_name="escrowed_balances", null=True
    )

    is_error = fields.BooleanField(default=False)
    claim_error = fields.TextField(null=True)

    user_member: fields.ForeignKeyRelation[
        "OrganizationMembership"
    ] = fields.ForeignKeyField(
        model_name="models.OrganizationMembership", related_name="user_funds"
    )

    balance_date = fields.DatetimeField(default=datetime.datetime.utcnow)
    claim_date = fields.DatetimeField(null=True)
