from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

import datetime


class User(models.Model):
    id = fields.IntField(pk=True)

    email = fields.CharField(max_length=128, unique=True)
    stake_address = fields.CharField(max_length=128, unique=True)
    token = fields.CharField(max_length=256, null=True)

    # If the current user is active / verified
    active = fields.BooleanField(default=False)

    register_date = fields.DatetimeField(default=datetime.datetime.utcnow)

    class PydanticMeta:
        exclude = ["id", "token"]

UserSpec = pydantic_model_creator(User, name="User")
UserInSpec = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)