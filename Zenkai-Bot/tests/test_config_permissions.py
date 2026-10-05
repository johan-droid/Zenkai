import asyncio
import json
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from zenkai.core.config import Settings
from zenkai.core.errors import PermissionDeniedError
from zenkai.core.permissions import Capability, PermissionMatrix


class Role:
    def __init__(self, role_id: int) -> None:
        self.id = role_id


class Member:
    def __init__(self, member_id: int, role_ids: list[int]) -> None:
        self.id = member_id
        self.roles = [Role(role_id) for role_id in role_ids]


def test_settings_reads_runtime_values() -> None:
    settings = Settings(
        _env_file=None,
        discord_token="token",
        database_url="sqlite+aiosqlite:///./test.db",
        environment="test",
    )

    assert settings.discord_token == "token"
    assert settings.environment == "test"
    assert settings.is_production is False


def test_settings_requires_token_for_runtime() -> None:
    settings = Settings(_env_file=None, discord_token="")

    with pytest.raises(ValueError, match="DISCORD_TOKEN"):
        settings.require_discord_token()


def test_main_reports_invalid_settings_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from zenkai.main import main

    def invalid_settings() -> Settings:
        raise ValidationError.from_exception_data(
            "Settings",
            [
                {
                    "type": "literal_error",
                    "loc": ("environment",),
                    "input": "invalid",
                    "ctx": {"expected": "'development', 'test', 'production'"},
                    "msg": "Input should be 'development', 'test', or 'production'",
                }
            ],
        )

    monkeypatch.setattr("zenkai.core.config.get_settings", invalid_settings)

    assert main([]) == 1
    captured = capsys.readouterr()
    payload = json.loads(captured.err.strip().splitlines()[-1])

    assert payload["message"] == "configuration_invalid"
    assert "environment" in payload["detail"]
    assert "Traceback" not in captured.err


def test_run_cleans_resources_after_partial_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zenkai.main import run

    database = Mock(initialize=AsyncMock(), close=AsyncMock())
    cache = Mock(close=AsyncMock())
    scheduler = Mock(start=Mock(), shutdown=AsyncMock())
    monkeypatch.setattr("zenkai.core.database.Database", lambda _url: database)
    monkeypatch.setattr("zenkai.core.cache.build_cache", lambda _url: cache)
    monkeypatch.setattr("zenkai.core.scheduler.SchedulerService", lambda: scheduler)
    monkeypatch.setattr(
        "zenkai.core.discord.client.ZenkaiBot",
        Mock(side_effect=RuntimeError("bot construction failed")),
    )
    settings = Settings(_env_file=None, discord_token="token", environment="test")

    with pytest.raises(RuntimeError, match="bot construction failed"):
        asyncio.run(run(settings))

    cache.close.assert_awaited_once()
    scheduler.shutdown.assert_awaited_once()
    database.close.assert_awaited_once()


def test_run_preserves_startup_error_when_cleanup_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zenkai.main import run

    database = Mock(initialize=AsyncMock(), close=AsyncMock())
    cache = Mock(close=AsyncMock())
    scheduler = Mock(start=Mock(), shutdown=AsyncMock())
    bot = Mock(
        start=AsyncMock(side_effect=RuntimeError("startup failed")),
        close=AsyncMock(side_effect=RuntimeError("cleanup failed")),
    )
    monkeypatch.setattr("zenkai.core.database.Database", lambda _url: database)
    monkeypatch.setattr("zenkai.core.cache.build_cache", lambda _url: cache)
    monkeypatch.setattr("zenkai.core.scheduler.SchedulerService", lambda: scheduler)
    monkeypatch.setattr("zenkai.core.discord.client.ZenkaiBot", lambda *_args, **_kwargs: bot)
    settings = Settings(_env_file=None, discord_token="token", environment="test")

    with pytest.raises(RuntimeError, match="startup failed") as startup:
        asyncio.run(run(settings))

    assert "cleanup failed" in "\n".join(startup.value.__notes__)


def test_permission_matrix_uses_hierarchical_capabilities() -> None:
    matrix = PermissionMatrix(
        role_map={
            Capability.SUPPORT: frozenset({10}),
            Capability.MODERATOR: frozenset({20}),
        }
    )
    member = Member(1, [20])

    assert Capability.MODERATOR in matrix.capabilities_for(member)
    assert matrix.can(member, Capability.SUPPORT)
    assert matrix.can(member, Capability.ADMIN) is False

    with pytest.raises(PermissionDeniedError):
        matrix.require(member, Capability.ADMIN)


def test_owner_bypasses_role_mapping() -> None:
    matrix = PermissionMatrix(owner_id=99)
    member = Member(99, [])

    assert matrix.can(member, Capability.OWNER)
