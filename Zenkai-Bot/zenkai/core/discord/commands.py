from dataclasses import dataclass, field
from typing import Any

from zenkai.core.permissions import Capability


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    name: str
    description: str
    required_capability: Capability = Capability.MEMBER
    cooldown_seconds: float = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class CommandRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, CommandDefinition] = {}

    def register(self, definition: CommandDefinition) -> None:
        if definition.name in self._definitions:
            raise ValueError(f"Command already registered: {definition.name}")
        self._definitions[definition.name] = definition

    def get(self, name: str) -> CommandDefinition | None:
        return self._definitions.get(name)

    def all(self) -> tuple[CommandDefinition, ...]:
        return tuple(self._definitions.values())
