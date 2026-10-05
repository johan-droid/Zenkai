import pytest

from zenkai.core.scheduler import JobDefinition, SchedulerService


async def sample_job() -> None:
    return None


def test_scheduler_registers_and_removes_jobs() -> None:
    scheduler = SchedulerService()
    definition = JobDefinition(
        id="test.job",
        handler=sample_job,
        trigger="interval",
        trigger_args={"seconds": 30},
    )

    scheduler.register(definition)

    assert "test.job" in scheduler.registered_ids
    assert scheduler.remove("test.job") is True
    assert scheduler.remove("test.job") is False


@pytest.mark.asyncio
async def test_scheduler_can_shutdown_when_not_started() -> None:
    scheduler = SchedulerService()
    await scheduler.shutdown()
