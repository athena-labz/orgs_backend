from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from lib import utils

from enum import Enum

import datetime


# Register
class UserType(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ORGANIZER = "organizer"


class User(models.Model):
    id = fields.IntField(pk=True)

    type = fields.CharField(max_length=16)
    email = fields.CharField(max_length=128, unique=True)
    stake_address = fields.CharField(max_length=128, unique=True)
    token = fields.CharField(max_length=256, null=True)

    # If the current user is active / verified
    active = fields.BooleanField(default=False)
    email_validation_string = fields.CharField(
        max_length=128, default=utils.string_generator
    )

    register_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id", "token", "email_validation_string"]


UserSpec = pydantic_model_creator(User, name="User")


class OrganizationType(Enum):
    GROUPS = "groups"
    INDIVIDUAL = "individual"


class Organization(models.Model):
    id = fields.IntField(pk=True)
    identifier = fields.CharField(max_length=64, unique=True, index=True)

    type = fields.CharField(max_length=16)
    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=512)

    students_password = fields.CharField(max_length=32)
    teachers_password = fields.CharField(max_length=32)

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

    user: fields.OneToOneRelation[User] = fields.OneToOneField(
        "models.User", related_name="organization_membership"
    )

    join_date = fields.DatetimeField(default=datetime.datetime.utcnow)

# OrganizationMembership - user - organization many to many