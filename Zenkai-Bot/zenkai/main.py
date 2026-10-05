from __future__ import annotations

import argparse
import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zenkai.core.config import Settings

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zenkai", description="Run the Zenkai Discord bot")
    parser.add_argument("--version", action="store_true", help="Print the Zenkai version")
    return parser


async def run(settings: Settings) -> None:
    from zenkai.core.cache import Cache, build_cache
    from zenkai.core.database import Database
    from zenkai.core.discord.client import ZenkaiBot
    from zenkai.core.permissions import PermissionMatrix
    from zenkai.core.scheduler import SchedulerService
    from zenkai.core.status import HealthRegistry, HealthState

    database = Database(settings.database_url)
    cache: Cache | None = None
    scheduler: SchedulerService | None = None
    bot: ZenkaiBot | None = None
    try:
        await database.initialize()
        health = HealthRegistry()
        health.update("database", HealthState.OPERATIONAL)
        cache = build_cache(settings.redis_connection_url)
        scheduler = SchedulerService()
        scheduler.start()
        health.update("scheduler", HealthState.OPERATIONAL)
        bot = ZenkaiBot(
            settings,
            database=database,
            scheduler=scheduler,
            cache=cache,
            health=health,
            permissions=PermissionMatrix(),
        )
        await bot.start(settings.require_discord_token())
    except BaseException as startup_error:
        cleanup_errors: list[BaseException] = []
        if bot is not None:
            try:
                await bot.close()
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
        else:
            if scheduler is not None:
                try:
                    await scheduler.shutdown()
                except BaseException as cleanup_error:
                    cleanup_errors.append(cleanup_error)
            if cache is not None:
                try:
                    await cache.close()
                except BaseException as cleanup_error:
                    cleanup_errors.append(cleanup_error)
            try:
                await database.close()
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
        for cleanup_failure in cleanup_errors:
            startup_error.add_note(f"Resource cleanup failed: {cleanup_failure!r}")
        raise
    else:
        assert bot is not None
        await bot.close()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.version:
        from zenkai import __version__

        print(__version__)
        return 0

    from pydantic import ValidationError

    from zenkai.core.config import get_settings
    from zenkai.core.errors import ZenkaiError
    from zenkai.core.logging import configure_logging

    configure_logging()
    try:
        settings = get_settings()
    except ValidationError as exc:
        detail = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors(include_url=False, include_input=False)
        )
        logger.error("configuration_invalid", extra={"detail": detail})
        return 1
    configure_logging(settings.log_level)
    if not settings.discord_token:
        logger.error(
            "discord_token_missing",
            extra={
                "hint": "Copy .env.example to .env and set DISCORD_TOKEN before starting Zenkai.",
            },
        )
        return 2

    try:
        asyncio.run(run(settings))
    except KeyboardInterrupt:
        logger.info("shutdown_requested")
    except ZenkaiError as exc:
        logger.error("startup_failed", extra={"detail": str(exc)})
        return 1
    except Exception:
        logger.exception("runtime_failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
