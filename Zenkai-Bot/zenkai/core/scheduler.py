from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, cast

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from zenkai.core.errors import ConfigurationError


@dataclass(frozen=True, slots=True)
class JobDefinition:
    id: str
    handler: Callable[..., Awaitable[Any]]
    trigger: str = "interval"
    trigger_args: Mapping[str, Any] = field(default_factory=dict)
    replace_existing: bool = True
    coalesce: bool = True
    max_instances: int = 1
    per_server: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ConfigurationError("Scheduler job id cannot be empty")


class SchedulerService:
    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._definitions: dict[str, JobDefinition] = {}

    def register(self, definition: JobDefinition) -> None:
        if definition.id in self._definitions:
            raise ConfigurationError(f"Scheduler job already registered: {definition.id}")
        self._scheduler.add_job(
            definition.handler,
            trigger=definition.trigger,
            args=(),
            kwargs={},
            id=definition.id,
            name=definition.id,
            replace_existing=definition.replace_existing,
            coalesce=definition.coalesce,
            max_instances=definition.max_instances,
            **dict(definition.trigger_args),
        )
        self._definitions[definition.id] = definition

    def register_many(self, definitions: list[JobDefinition]) -> None:
        for definition in definitions:
            self.register(definition)

    def remove(self, job_id: str) -> bool:
        if job_id not in self._definitions:
            return False
        self._scheduler.remove_job(job_id)
        self._definitions.pop(job_id, None)
        return True

    @property
    def registered_ids(self) -> frozenset[str]:
        return frozenset(self._definitions)

    @property
    def running(self) -> bool:
        return cast(bool, self._scheduler.running)

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()

    async def shutdown(self, *, wait: bool = True) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)
