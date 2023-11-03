from tortoise.expressions import Q
from model import OrganizationMembership, Group, GroupMembership, User


async def is_member_of_group(membership: OrganizationMembership):
    # Make sure user is not member of existing group form this organization
    existing_group_membership = await GroupMembership.filter(
        Q(user=membership.user)
        & Q(group__organization=membership.organization)
        & Q(accepted=True)
    ).first()
    
    return existing_group_membership is not None
