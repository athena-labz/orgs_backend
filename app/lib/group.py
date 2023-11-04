from tortoise.expressions import Q
from model import OrganizationMembership, Group, GroupMembership, User


async def get_user_group_membership(membership: OrganizationMembership):
    existing_group_membership = await GroupMembership.filter(
        Q(user=membership.user)
        & Q(group__organization=membership.organization)
        & Q(accepted=True)
    ).first()

    return existing_group_membership


async def is_member_of_group(membership: OrganizationMembership):
    existing_group_membership = await get_user_group_membership(membership)

    return existing_group_membership is not None


async def is_member_of_specific_group(membership: OrganizationMembership, group: Group):
    # Make sure user is not member of existing group form this organization
    existing_group_membership = await GroupMembership.filter(
        Q(user=membership.user) & Q(group=group) & Q(accepted=True)
    ).first()

    return existing_group_membership is not None
