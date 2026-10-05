from zenkai.core.status import HealthRegistry, HealthState


def test_empty_health_is_unavailable() -> None:
    snapshot = HealthRegistry().snapshot()

    assert snapshot == {"overall": "unavailable", "services": {}}


def test_health_snapshot_reports_worst_state() -> None:
    registry = HealthRegistry()
    registry.update("database", HealthState.OPERATIONAL)
    registry.update("ai", HealthState.DEGRADED)
    registry.update("anime", HealthState.UNAVAILABLE)

    snapshot = registry.snapshot()

    assert snapshot["overall"] == "unavailable"
    assert snapshot["services"]["anime"]["state"] == "unavailable"
