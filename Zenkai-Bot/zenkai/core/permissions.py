from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Protocol

from zenkai.core.errors import PermissionDeniedError


class Capability(IntEnum):
    MEMBER = 0
    SUPPORT = 1
    EVENT_MANAGER = 2
    MODERATOR = 3
    ADMIN = 4
    OWNER = 5


class RoleLike(Protocol):
    @property
    def id(self) -> int: ...


class MemberLike(Protocol):
    @property
    def id(self) -> int: ...

    @property
    def roles(self) -> Iterable[RoleLike]: ...


@dataclass(frozen=True, slots=True)
class PermissionMatrix:
    role_map: Mapping[Capability, frozenset[int]] = field(default_factory=dict)
    owner_id: int | None = None

    def capabilities_for(self, member: MemberLike) -> set[Capability]:
        capabilities = {Capability.MEMBER}
        member_role_ids = {role.id for role in member.roles}
        for capability, role_ids in self.role_map.items():
            if member_role_ids.intersection(role_ids):
                capabilities.add(capability)
        if self.owner_id is not None and member.id == self.owner_id:
            capabilities.add(Capability.OWNER)
        return capabilities

    def can(self, member: MemberLike, required: Capability) -> bool:
        return max(self.capabilities_for(member)) >= required

    def require(self, member: MemberLike, required: Capability) -> None:
        if not self.can(member, required):
            action = required.name.lower()
            raise PermissionDeniedError(
                f"{required.name} capability is required",
                user_message=f"You do not have permission to use that {action} action.",
            )


def can_assign_role(
    bot_top_role_position: int,
    target_role_position: int,
    *,
    has_manage_roles: bool,
) -> bool:
    return has_manage_roles and bot_top_role_position > target_role_position
