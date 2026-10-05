---
tags: [zenkai, memory, project]
status: active
created: 2026-09-24
updated: 2026-09-24
---

# Zenkai Project Memory

## Product Intent

Zenkai is one coherent Discord community assistant, not a collection of unrelated bots. It should provide useful anime-community functionality with clear boundaries and reliable failure behavior.

## Architecture Decisions

- Discord is the only platform.
- Slash commands, buttons, select menus, and modals are the primary interaction surfaces.
- AI assists with generation, classification, and suggestions; authorized humans control moderation and administration.
- Time-based behavior is deterministic and scheduler-driven.
- Features are configured independently per Discord server.
- External providers sit behind small interfaces.
- Secrets never enter logs, backups, generated content, or vault notes.

## Current Implementation

- Python 3.12 project created at `../../Zenkai-Bot/`.
- Core configuration, JSON logging, error hierarchy, async database access, memory/Redis cache, shared scheduler, permission matrix, health registry, and Discord client are implemented.
- Slash command `/ping` is registered as the canary interaction.
- Foundational tests, Ruff, mypy, and a local runtime smoke test pass.
- Discord gateway connection remains pending a valid local `DISCORD_TOKEN`.

## Open Work

- Complete Plan 1 Discord integration verification.
- Implement Plan 2 community features.
- Add database repositories and migration files for the first real feature.
- Configure the vault MCP in the local MCP client.
- Keep project memory current after each implementation milestone.

## Update Format

Use the `append_project_memory` MCP tool for timestamped updates. Keep entries short, factual, and explicit about status or decisions.

## 2026-09-24 17:49 UTC

MCP integration verified against the local vault.

## 2026-09-24 17:53 UTC

Repository organization updated: project documentation is centralized in Zenkai-Vault, the filesystem-backed zenkai-vault MCP server is available in Zenkai-MCP, and project-level OpenCode access is configured in opencode.json with agent guidance in AGENTS.md. Next step: restart OpenCode and verify the zenkai-vault tools are available to the agent.

## 2026-09-24 17:54 UTC

Repository hygiene and agent access updated: root .gitignore now excludes secrets, virtual environments, generated caches, databases, and local Obsidian workspace state. opencode.json now registers the local zenkai-vault MCP with a stable project-relative working directory, and AGENTS.md defines vault-first agent behavior.

## 2026-09-24 17:54 UTC

Verification complete: opencode.json and MCP config parse successfully, all vault and repository links resolve, the MCP package passes 4 tests and Ruff, the stdio server starts with the project configuration, and generated cache directories were removed while local virtual environments and uv.lock were retained.

## 2026-09-24 19:27 UTC

Implementation audit completed against the execution plan, architecture phases, MVP, and definition of done. Plan 0 is complete and locally verified. Plan 1 remains partial: Discord gateway `/ping` is unverified, architecture-required migrations/models/repositories, event bus, durable/recoverable scheduler use, audit writer, per-guild defaults/configuration, interaction plumbing, capability-enforced dispatch, health endpoint, and deployment assets are absent. Plans 2–9 have no feature implementations. Verification passed: bot 8 tests, Ruff, mypy (16 files), CLI help; MCP 4 tests and Ruff. Current checks do not establish feature completion or production readiness. Next step is to complete Plan 1 acceptance before starting Plan 2.

## 2026-09-24 19:56 UTC

2026-09-24 19:56 UTC — Completed a read-only audit of the current bot and vault MCP implementation. Verification passed: bot 8 tests, CLI help/version, Ruff, mypy, and `uv pip check`; MCP 4 tests and Ruff. Reproduced three control gaps: `JsonFormatter` emitted a sentinel token embedded in a log message, an empty `HealthRegistry` reported `operational`, and invalid `ENVIRONMENT` exited with an uncaught Pydantic traceback before startup error handling. `python -m zenkai_vault_mcp` exits without starting the server, and neither component has Git metadata. Discord gateway verification remains blocked because no local `.env` or token is present. Current bot remains foundation/canary-only: no features, migrations, repositories, event bus, capability-enforced dispatch, production jobs, health endpoint, or deployment assets. Next gate: fix these Plan 1 controls, add focused regression tests, then verify `/ping` in a staging guild before Plan 2.

## 2026-09-25 07:50 UTC

2026-09-25 deep read-only audit completed across Zenkai-Bot, Zenkai-MCP, README files, architecture, execution plan, and operations notes. Fresh verification passed: bot 8 tests, Ruff, mypy, CLI help/version, uv dependency check, and database init/ping smoke; MCP 4 tests, Ruff, uv lock check, and a real stdio initialize plus vault_info handshake. Confirmed findings: JsonFormatter leaks secrets embedded in messages and exception text; Settings validation occurs outside the startup error handler; empty HealthRegistry reports operational; MemoryCache ttl_seconds=0 persists while Redis rejects it; NullCache is not interchangeable with the JSON API; Message Content intent is unnecessary for the current slash-only bot; MCP blank ZENKAI_VAULT_PATH targets cwd; MCP python -m entrypoint exits without starting; current bot has no models, migrations, repositories, event bus, audit writer, production scheduler jobs, permission-enforced dispatch, health endpoint, or feature implementations. Discord gateway /ping and unauthorized-command behavior remain unverified. The execution plan's checked Plan 1 task list and later partial-audit table conflict; the partial-audit assessment is accurate. No source files were modified.

## 2026-09-25 09:22 UTC

2026-09-25 — Completed the focused Plan 1 bot bug-fix pass. Root causes fixed in runtime source: JsonFormatter now redacts labeled secrets, URL userinfo including password-only Redis URLs, raw Bearer/Basic values, exception text, nested values, and bytes; main configures bootstrap logging before settings validation and preserves startup failures during cleanup; empty health is unavailable; cache Protocol/NullCache and TTL semantics are consistent; Message Content intent is disabled; ZenkaiBot injects PermissionMatrix and wraps registered callbacks with capability enforcement and existing ephemeral error UX; startup/shutdown resource cleanup attempts every dependency and preserves the primary exception. Added focused regression tests. Verification passed: 21 pytest, Ruff, mypy 16 source files, CLI help/version, in-memory database smoke, and uv pip check. Live Discord gateway and staging admin-denial checks remain pending a valid token/guild. Next step: continue Plan 1 acceptance work only after staging verification; Plans 2–9 are not implemented.
