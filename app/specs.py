from pydantic import BaseModel, Field
from typing import Annotated
from enum import Enum
from model import UserSpec, OrganizationType, OrganizationSpec, UserType


# Token
class TokenSpec(BaseModel):
    access_token: str
    token_type: str


class TokenDataSpec(BaseModel):
    username: str | None = None


class RegisterBodySpec(BaseModel):
    user_type: UserType
    email: Annotated[str, Field(max_length=128)]
    stake_address: Annotated[str, Field(max_length=128)]
    signature: str


class CreateOrganizationBodySpec(BaseModel):
    organization_type: OrganizationType
    identifier: Annotated[str, Field(max_length=64)]
    name: Annotated[str, Field(max_length=128)]
    description: Annotated[str, Field(max_length=512)]
    students_password: Annotated[str, Field(max_length=32)]
    teachers_password: Annotated[str, Field(max_length=32)]
    areas: Annotated[list[str], Field(max_length=10)]
