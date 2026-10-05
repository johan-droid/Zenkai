from unittest.mock import AsyncMock, Mock

import discord
import pytest

from zenkai.core.cache import MemoryCache
from zenkai.core.config import Settings
from zenkai.core.database import Database
from zenkai.core.discord.client import ZenkaiBot
from zenkai.core.discord.commands import CommandDefinition
from zenkai.core.errors import PermissionDeniedError
from zenkai.core.permissions import Capability, PermissionMatrix
from zenkai.core.scheduler import SchedulerService
from zenkai.core.status import HealthRegistry


def build_bot(permissions: PermissionMatrix) -> ZenkaiBot:
    return ZenkaiBot(
        Settings(_env_file=None, discord_token="test-token"),
        database=Database("sqlite+aiosqlite:///:memory:"),
        scheduler=SchedulerService(),
        cache=MemoryCache(),
        health=HealthRegistry(),
        permissions=permissions,
    )


def build_interaction(member: object) -> Mock:
    interaction = Mock(spec=discord.Interaction)
    interaction.guild = Mock()
    interaction.user = member
    interaction.response = AsyncMock()
    interaction.response.is_done = Mock(return_value=False)
    interaction.followup = AsyncMock()
    return interaction


def build_member(member_id: int, role_ids: list[int]) -> Mock:
    member = Mock(spec=discord.Member)
    member.id = member_id
    member.roles = [Mock(id=role_id) for role_id in role_ids]
    return member


def test_bot_does_not_request_message_content_intent() -> None:
    bot = build_bot(PermissionMatrix())

    assert bot.intents.message_content is False


@pytest.mark.asyncio
async def test_command_dispatch_enforces_capability_and_ephemeral_denial() -> None:
    bot = build_bot(PermissionMatrix(role_map={Capability.ADMIN: frozenset({20})}))
    handled = False

    async def handler(interaction: discord.Interaction) -> None:
        nonlocal handled
        handled = True

    bot._register_command(
        CommandDefinition("admin", "Admin action", required_capability=Capability.ADMIN),
        handler,
    )
    command = bot.tree.get_command("admin")
    denied_interaction = build_interaction(build_member(1, []))

    assert command is not None
    with pytest.raises(PermissionDeniedError) as denied:
        await command.callback(denied_interaction)
    await bot._on_app_command_error(denied_interaction, denied.value)

    assert handled is False
    denied_interaction.response.send_message.assert_awaited_once_with(
        "You do not have permission to use that admin action.",
        ephemeral=True,
    )

    await command.callback(build_interaction(build_member(2, [20])))
    assert handled is True


@pytest.mark.asyncio
async def test_command_dispatch_attempts_every_cleanup_after_failure() -> None:
    bot = build_bot(PermissionMatrix())
    bot.scheduler = Mock(shutdown=AsyncMock())
    bot.cache = Mock(close=AsyncMock(side_effect=RuntimeError("cache close failed")))
    bot.database = Mock(close=AsyncMock(side_effect=RuntimeError("database close failed")))

    with pytest.raises(ExceptionGroup) as cleanup:
        await bot.close()

    assert {str(error) for error in cleanup.value.exceptions} == {
        "cache close failed",
        "database close failed",
    }
    bot.scheduler.shutdown.assert_awaited_once()
    bot.cache.close.assert_awaited_once()
    bot.database.close.assert_awaited_once()
