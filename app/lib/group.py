from tortoise.expressions import Q
from model import OrganizationMembership, Group, GroupMembership, User


async def is_member_of_group(membership: OrganizationMembership):
    # Make sure user is not member of existing group
    existing_group_membership = await GroupMembership.filter(
        Q(user_membership=membership) & Q(accepted=True)
    ).first()
    if existing_group_membership is not None:
        return True
    
    return False