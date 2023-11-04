from pydantic import BaseModel, Field
from typing import Annotated, Optional
from model import (
    UserSpec,
    OrganizationType,
    OrganizationSpec,
    UserType,
    GroupSpec,
    TaskSpec,
)

import datetime


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


class EditOrganizationBodySpec(BaseModel):
    organization_type: Optional[OrganizationType] = None
    name: Optional[Annotated[str, Field(max_length=128)]] = None
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    students_password: Optional[Annotated[str, Field(max_length=32)]] = None
    teachers_password: Optional[Annotated[str, Field(max_length=32)]] = None
    areas: Optional[Annotated[list[str], Field(max_length=10)]] = None


class JoinOrganizationBodySpec(BaseModel):
    password: str
    area: Optional[Annotated[str, Field(max_length=64, null=True)]] = None


class CreateGroupBodySpec(BaseModel):
    identifier: Annotated[str, Field(max_length=64, pattern=r"^[a-zA-Z0-9_-]{1,50}$")]
    name: Annotated[str, Field(max_length=128)]
    leader_reward: int
    members: Annotated[
        dict[str, int], Field(max_length=4, min_length=1)
    ]  # map of stake address and reward


class CreateTaskBodySpec(BaseModel):
    identifier: Annotated[str, Field(max_length=64, pattern=r"^[a-zA-Z0-9_-]{1,50}$")]
    name: Annotated[str, Field(max_length=128)]
    description: Annotated[str, Field(max_length=1024)]
    deadline: datetime.datetime


class SubmitTaskBodySpec(BaseModel):
    name: Annotated[str, Field(max_length=128)]
    description: Annotated[str, Field(max_length=1024)]


class RejectTaskBodySpec(BaseModel):
    description: Annotated[str, Field(max_length=1024)]


class ReviewTaskBodySpec(BaseModel):
    description: Annotated[str, Field(max_length=1024)]
    extended_deadline: Optional[datetime.datetime] = None


class ListResponse(BaseModel):
    current_page: int
    max_page: int


class UserTasksResponse(ListResponse):
    tasks: list[TaskSpec]


class OrganizationUsersResponse(ListResponse):
    users: list[UserSpec]
