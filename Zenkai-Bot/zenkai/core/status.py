from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class HealthState(StrEnum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class HealthEntry:
    service: str
    state: HealthState
    message: str = ""
    latency_ms: float | None = None
    checked_at: str = ""


class HealthRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, HealthEntry] = {}

    def update(
        self,
        service: str,
        state: HealthState,
        *,
        message: str = "",
        latency_ms: float | None = None,
    ) -> None:
        from datetime import UTC, datetime

        self._entries[service] = HealthEntry(
            service=service,
            state=state,
            message=message,
            latency_ms=latency_ms,
            checked_at=datetime.now(UTC).isoformat(),
        )

    def snapshot(self) -> dict[str, Any]:
        states = [entry.state for entry in self._entries.values()]
        if not states:
            overall = HealthState.UNAVAILABLE
        elif HealthState.UNAVAILABLE in states:
            overall = HealthState.UNAVAILABLE
        elif HealthState.DEGRADED in states:
            overall = HealthState.DEGRADED
        else:
            overall = HealthState.OPERATIONAL
        return {
            "overall": overall.value,
            "services": {
                name: {
                    "state": entry.state.value,
                    "message": entry.message,
                    "latency_ms": entry.latency_ms,
                    "checked_at": entry.checked_at,
                }
                for name, entry in sorted(self._entries.items())
            },
        }
