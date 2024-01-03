from pydantic import BaseModel, Field
from typing import Annotated, Optional
from app.model import (
    UserSpec,
    OrganizationSpec,
    UserType,
    GroupSpec,
    GroupMembershipSpec,
    TaskSpec,
    TaskActionSpec
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


class UserAddPaymentAddressBodySpec(BaseModel):
    address: str


class CreateOrganizationBodySpec(BaseModel):
    identifier: Annotated[str, Field(max_length=64)]
    name: Annotated[str, Field(max_length=128)]
    description: Annotated[str, Field(max_length=512)]
    students_password: Annotated[str, Field(max_length=32)]
    teachers_password: Annotated[str, Field(max_length=32)]
    supervisor_password: Annotated[str, Field(max_length=32)]
    areas: Annotated[list[str], Field(max_length=10)]


class EditOrganizationBodySpec(BaseModel):
    name: Optional[Annotated[str, Field(max_length=128)]] = None
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    students_password: Optional[Annotated[str, Field(max_length=32)]] = None
    teachers_password: Optional[Annotated[str, Field(max_length=32)]] = None
    supervisor_password: Optional[Annotated[str, Field(max_length=32)]] = None
    areas: Optional[Annotated[list[str], Field(max_length=10)]] = None


class JoinOrganizationBodySpec(BaseModel):
    password: str
    area: Optional[Annotated[str, Field(max_length=64, null=True)]] = None


class CreateGroupBodySpec(BaseModel):
    identifier: Annotated[str, Field(max_length=64, pattern=r"^[a-zA-Z0-9_-]{1,50}$")]
    name: Annotated[str, Field(max_length=128)]
    members: Annotated[
        list[str], Field(max_length=4, min_length=1)
    ]  # list of emails


class CreateTaskBodySpec(BaseModel):
    identifier: Annotated[str, Field(max_length=64, pattern=r"^[a-zA-Z0-9_-]{1,50}$")]
    name: Annotated[str, Field(max_length=128)]
    description: Annotated[str, Field(max_length=1024)]
    rewards: dict[str, int]  # map of stake address to reward
    deadline: datetime.datetime


class CreateIndividualTaskBodySpec(BaseModel):
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


class FundTaskBodySpec(BaseModel):
    amount: int


class ListResponse(BaseModel):
    current_page: int
    max_page: int


class TasksResponse(ListResponse):
    tasks: list[TaskSpec]


class TaskActionsResponse(ListResponse):
    actions: list[TaskActionSpec]


class OrganizationUsersResponse(ListResponse):
    users: list[UserSpec]


class UserOrganizationsResponse(ListResponse):
    organizations: list[OrganizationSpec]


class GroupMembershipExtendedSpec(GroupMembershipSpec):
    group: GroupSpec


class OrganizationGroupsResponse(ListResponse):
    groups: list[GroupMembershipExtendedSpec]


class BalanceResponse(BaseModel):
    owed: int
    available: int
    escrowed: int
    claimed: int
    last_claim_date: Optional[datetime.datetime]
