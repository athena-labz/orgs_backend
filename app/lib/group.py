from tortoise.expressions import Q
from model import OrganizationMembership, Group, GroupMembership, User


async def is_member_of_group(user: User, membership: OrganizationMembership):
    # Make sure user is not leader_membership of existing group
    existing_group = await Group.filter(leader_membership=membership).first()
    if existing_group is not None:
        return True

    # Make sure user is not member of existing group
    existing_group_membership = await GroupMembership.filter(
        Q(user_membership=membership) & Q(accepeted=True)
    ).first()
    if existing_group_membership is not None:
        return True
    
    return False