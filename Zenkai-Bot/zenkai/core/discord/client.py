import logging
import time
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from zenkai.core.cache import Cache
from zenkai.core.config import Settings
from zenkai.core.database import Database
from zenkai.core.discord.commands import CommandDefinition, CommandRegistry
from zenkai.core.errors import PermissionDeniedError, ZenkaiError
from zenkai.core.permissions import PermissionMatrix
from zenkai.core.scheduler import SchedulerService
from zenkai.core.status import HealthRegistry, HealthState

logger = logging.getLogger(__name__)


class ZenkaiBot(commands.Bot):
    def __init__(
        self,
        settings: Settings,
        *,
        database: Database,
        scheduler: SchedulerService,
        cache: Cache,
        health: HealthRegistry,
        permissions: PermissionMatrix,
    ) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="", intents=intents, help_command=None)
        self.settings = settings
        self.database = database
        self.scheduler = scheduler
        self.cache = cache
        self.health = health
        self.permissions = permissions
        self.registry = CommandRegistry()
        self._started_at = time.monotonic()
        setattr(self.tree, "on_error", self._on_app_command_error)
        self._register_canary()

    async def setup_hook(self) -> None:
        guild_id = self.settings.guild_id_int
        guild = discord.Object(id=guild_id) if guild_id else None
        await self.tree.sync(guild=guild)
        self.health.update("discord_gateway", HealthState.OPERATIONAL)
        logger.info("discord_commands_synced", extra={"guild_id": self.settings.guild_id_int})

    async def on_ready(self) -> None:
        self.health.update("discord_gateway", HealthState.OPERATIONAL)
        logger.info("discord_ready", extra={"user_id": self.user.id if self.user else None})

    def _register_command(self, definition: CommandDefinition, callback: Any) -> None:
        self.registry.register(definition)

        async def dispatch(interaction: discord.Interaction) -> None:
            member = interaction.user
            if interaction.guild is None or not isinstance(member, discord.Member):
                raise PermissionDeniedError("A guild member is required")
            self.permissions.require(member, definition.required_capability)
            await callback(interaction)

        self.tree.add_command(
            app_commands.Command(
                name=definition.name,
                description=definition.description,
                callback=dispatch,
            )
        )

    def _register_canary(self) -> None:
        definition = CommandDefinition(
            name="ping",
            description="Check whether Zenkai is online.",
        )

        async def ping(interaction: discord.Interaction) -> None:
            latency_ms = round(self.latency * 1000)
            uptime_seconds = round(time.monotonic() - self._started_at)
            await interaction.response.send_message(
                f"Zenkai is online. Gateway latency: {latency_ms} ms. Uptime: {uptime_seconds}s.",
                ephemeral=True,
            )

        self._register_command(definition, ping)

    async def _on_app_command_error(
        self,
        interaction: Any,
        error: Any,
    ) -> None:
        cause = error.__cause__ or error
        if isinstance(cause, ZenkaiError):
            message = cause.user_message
        else:
            logger.exception("app_command_failed", exc_info=error)
            message = "Zenkai could not complete that request. Please try again shortly."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    async def close(self) -> None:
        errors: list[BaseException] = []
        try:
            await super().close()
        except BaseException as exc:
            errors.append(exc)
        try:
            await self.scheduler.shutdown()
        except BaseException as exc:
            errors.append(exc)
        try:
            await self.cache.close()
        except BaseException as exc:
            errors.append(exc)
        try:
            await self.database.close()
        except BaseException as exc:
            errors.append(exc)
        if len(errors) == 1:
            raise errors[0]
        if errors:
            raise BaseExceptionGroup("Multiple shutdown failures", errors)
        logger.info("discord_runtime_closed")
