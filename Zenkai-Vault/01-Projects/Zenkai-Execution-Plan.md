# Zenkai Bot — Execution Plan

This file divides the entire execution of the Zenkai Discord bot into plans. Each plan is a
checkpoint with its own tasks, deliverables, and acceptance criteria. Work happens plan by plan,
in order, and each plan must meet its acceptance criteria before the next one starts.

The product architecture (features, workflows, MVP, definition of done) is defined in
`../02-Architecture/Zenkai-Architecture.md`. Every plan below references it.

Status legend:

- `[ ]` not started
- `[/]` in progress
- `[x]` done and verified

---

## Plan 0 — Project Bootstrap

**Goal:** Create a clean, runnable Python project skeleton with tooling, dependencies, and CI-ready checks.

Tasks:

- [x] Create the `Zenkai-Bot/` project folder
- [x] `pyproject.toml` with dependencies and tooling (discord.py, pydantic, SQLAlchemy, APScheduler)
- [x] `.env.example` documenting every configuration key
- [x] `.gitignore` (Python, env, cache, data, build artifacts)
- [x] `zenkai/` package layout: `core/`, `features/`
- [x] `tests/` harness with pytest
- [x] Minimal `python -m zenkai --help` that prints CLI options and exits clean

Acceptance criteria:

- [x] `python -m zenkai --help` works after `pip install -e .`
- [x] `pytest` discovers and passes foundational tests
- [x] The package imports without a Discord token

## Plan 1 — Foundation (Core) — **In progress**

**Goal:** Core infrastructure: configuration, logging, errors, database, cache, scheduler,
permissions, and the Discord runtime with command dispatch.

Tasks:

- [x] `core/config.py` — environment-driven settings with validation
- [x] `core/logging.py` — structured, redacted logging setup
- [x] `core/errors.py` — Zenkai error hierarchy and user-facing messages
- [x] `core/database.py` — async engine, sessions, health check, migration hook
- [x] `core/cache.py` — cache interface with no-op and Redis implementations
- [x] `core/scheduler.py` — shared scheduler wrapper with idempotent isolated jobs
- [x] `core/permissions.py` — capability levels mapped from Discord roles
- [x] `core/discord/` — bot client, command registry, canary `/ping` end-to-end
- [x] `main.py` — graceful startup (config → db → scheduler → bot) and shutdown
- [x] `core/status.py` — health aggregation for diagnostics

Acceptance criteria:

- [ ] Bot connects with a valid token and answers `/ping`
- [ ] Unauthorized use of admin commands is denied with an ephemeral message
- [x] Scheduler jobs survive registration without blocking the gateway
- [x] Configuration validation failures produce clear errors at startup
- [x] Unit tests cover config, permissions, cache, scheduler, and error mapping

## Plan 2 — Community

**Goal:** Welcome/leave, roles, XP/levels, streaks, profiles, badges, and statistics.

Tasks:

- [ ] `features/welcome/` — welcome/leave cards, message templates, join logs
- [ ] `features/roles/` — button/select role menus, auto-roles, level reward roles
- [ ] `features/leveling/` — XP pipeline, anti-abuse guards, levels, streaks
- [ ] `features/members/` — profiles, badges, achievements, member stats
- [ ] `features/statistics/` — rollups and leaderboards
- [ ] Bus events: `member.joined`, `member.left`, `xp.gained`, `level.up`, `streak.updated`

Acceptance criteria:

- [ ] A new member triggers welcome, auto-role, and stats increment
- [ ] XP is throttled; duplicate/spam/farming messages award zero and are audited
- [ ] Level ups assign configured roles respecting Discord hierarchy
- [ ] `/profile` renders a profile card from persisted data
- [ ] Statistics snapshots populate hourly/daily without duplication

## Plan 3 — Moderation and Support

**Goal:** Moderation tools, raid protection, tickets, suggestions, bug reports, and backups.

Tasks:

- [ ] `features/moderation/` — warn, timeout, kick, ban, slowmode, logs, history
- [ ] `features/moderation/` — raid protection thresholds and staff alerts
- [ ] `features/tickets/` — categories, claim/reopen/close, transcripts, auto-close
- [ ] `features/suggestions/` — suggestion lifecycle and voting
- [ ] `features/bugs/` — bug report lifecycle and duplicate detection
- [ ] `features/backup/` — configuration snapshots and guarded restore

Acceptance criteria:

- [ ] Every moderation action requires capability + hierarchy check and writes an audit row
- [ ] Tickets follow the state machine; inactivity auto-close is scheduler-driven
- [ ] Suggestions and bugs transition status only through staff capabilities
- [ ] Backups exclude secrets; restore requires explicit admin authorization

## Plan 4 — AI

**Goal:** AI tool suite, provider router, controlled chat, and safety boundaries.

Tasks:

- [ ] `features/ai/` — `/ask`, `/anime`, `/manga`, `/explain`, `/character`, `/summarize`
- [ ] `features/ai/` — `/suggest`, `/bug`, `/pollai`, `/modai`
- [ ] `features/ai/router.py` — provider router with fallback ordering
- [ ] `features/ai/chat.py` — mention/enabled-channel-only conversational chat
- [ ] `core/ai.py` — AIProvider interface and provider adapters
- [ ] Safety: hallucination guard, PII/invite/raid suppression, cost caps

Acceptance criteria:

- [ ] AI commands route through the provider interface, never provider-specific code
- [ ] Provider failure falls back to the next eligible provider
- [ ] `/modai` only produces staff alerts; it never acts autonomously
- [ ] Controlled chat responds only on mention, reply, explicit interaction, or enabled channel
- [ ] Summarizing private content requires a permission check

## Plan 5 — Anime

**Goal:** Anime/manga providers, news feed, and weekly/monthly awards.

Tasks:

- [ ] `core/providers/anime.py` — AnimeProvider interface + adapter + cache
- [ ] `features/anime/` — search, recommendations, random, characters, `/manga`
- [ ] `features/anime/news.py` — news polling with duplicate suppression
- [ ] `features/awards/` — award definitions, voting, scheduler closure, winners

Acceptance criteria:

- [ ] Provider adapter failures degrade one feature with a clear user message
- [ ] Zenkai never invents anime/manga facts; provider misses return "unknown"
- [ ] News feed does not repost duplicates
- [ ] Award winner selection is deterministic and audited

## Plan 6 — Entertainment

**Goal:** Games, polls, giveaways, events, and watch parties.

Tasks:

- [ ] `features/games/` — session engine, trivia, guess-the-character, Akinator, random
- [ ] `features/polls/` — custom, recurring, `/pollai`-generated polls
- [ ] `features/giveaways/` — entry, deterministic draw, reroll, eligibility
- [ ] `features/events/` — RSVP, reminders, attendance
- [ ] `features/watchparty/` — watch-party workflow and participation

Acceptance criteria:

- [ ] Games track wins/losses/high score and feed stats
- [ ] Giveaway winners draw deterministically and idempotently across restarts
- [ ] Polls close on scheduler timeouts; `/pollai` output is user-confirmed
- [ ] Events and watch parties send reminders exactly once

## Plan 7 — Automation

**Goal:** Notifications, live status monitoring, and scheduled announcements.

Tasks:

- [ ] `features/notifications/` — per-channel, per-kind notification service
- [ ] `features/status/` — external service monitoring with retry/confirmation
- [ ] Scheduler jobs for news, reminders, status, backups, and announcements

Acceptance criteria:

- [ ] Notifications respect quiet-hours, cooldowns, and permission checks
- [ ] Status alerts fire only after consecutive confirmed failures
- [ ] Missed scheduled jobs are handled on next startup without double effects

## Plan 8 — Dashboard and Ops

**Goal:** Admin dashboard, REST API, observability, and deployment.

Tasks:

- [ ] `dashboard/` — API server (FastAPI-style) with auth and per-section ACL
- [ ] Dashboard frontend sections (settings, tickets, analytics, backups)
- [ ] Health/status endpoints (`/health`)
- [ ] Deployment manifests and operational runbook

Acceptance criteria:

- [ ] Dashboard writes go through the same domain services as Discord interactions
- [ ] Every dashboard change is audited and emits `config.updated`
- [ ] Secrets are never returned by the API
- [ ] `/health` reports database, Redis, scheduler, AI provider, and anime provider

## Plan 9 — Hardening and Release

**Goal:** Tests, load checks, security review, and the MVP release.

Tasks:

- [ ] Full unit + integration coverage per feature
- [ ] Regression tests for every production bug
- [ ] Load tests for XP hot path and high-traffic servers
- [ ] Security review: permissions, secrets, AI safety, rate limits
- [ ] MVP release checklist and documentation pass

Acceptance criteria:

- [ ] Every feature meets the Definition of Done in `../02-Architecture/Zenkai-Architecture.md#47-definition-of-done`
- [ ] API rate limits and cooldowns verified under load
- [ ] Zero secrets in logs, backups, or restored config
- [ ] MVP scope defined in `../02-Architecture/Zenkai-Architecture.md#46-mvp` ships

---

## Cross-Plan Rules

1. Complete the definition of done before marking a task done.
2. One feature per integration surface; no cross-feature table mutations.
3. Deterministic time-based behavior lives in the scheduler, not in AI.
4. AI never performs administrative or moderation actions automatically.
5. Every production bug becomes a regression test.


## 2026-09-25 Audit

Status: in progress. Reviewing all planned Plans 0–9 against the current `Zenkai-Bot` and `Zenkai-MCP` implementations, architecture definition of done, tests, lint, type checking, and Discord verification status.



### Audit result — 2026-09-25

| Plan | Audited status | Evidence / remaining work |
| --- | --- | --- |
| 0 — Bootstrap | Complete and locally verified | Package, CLI, test harness, and dependencies work; `python -m zenkai --help`, 8 tests, Ruff, and mypy pass. |
| 1 — Foundation | Partial; acceptance not met | Core configuration, errors, cache variants, role-capability mapping, lifecycle, health registry, and `/ping` exist. Gateway `/ping` remains unverified without a token. Database uses `create_all` rather than Alembic migrations and has no models/repositories. Scheduler has no durable recovery, job metadata store, or registered production jobs. Event bus, audit writer, per-guild configuration/default seeding, interaction component plumbing, capability-enforced command dispatch, admin-denial coverage, health endpoint, Docker Compose, and architecture-required integration/regression coverage are absent. Error mapping is not unit-tested. |
| 2 — Community | Not started | `zenkai/features/` has no feature implementation. |
| 3 — Moderation and Support | Not started | No moderation, raid, ticket, suggestion, bug, or backup modules. |
| 4 — AI | Not started | Provider settings exist only as configuration; no provider interface, adapters, router, commands, or safety pipeline. |
| 5 — Anime | Not started | No provider interface, services, commands, news, or awards. |
| 6 — Entertainment | Not started | No games, polls, giveaways, events, or watch parties. |
| 7 — Automation | Not started | No notification or status services and no feature scheduler jobs. |
| 8 — Dashboard and Ops | Not started | No dashboard, API, health endpoint, deployment manifests, or runbook. |
| 9 — Hardening and Release | Not started | Foundational unit checks exist, but required feature integration, regression, load, rate-limit, security, and release verification do not. |

Verification run: bot `8 passed`, Ruff passed, mypy passed across 16 source files, and CLI help passed; MCP `4 passed` and Ruff passed. These checks prove the current foundation compiles and its narrow unit tests pass; they do not satisfy the architecture definition of done. No plan beyond Plan 0 meets production-verified completion.

Supporting `Zenkai-MCP` vault tooling is operational through its console entrypoint, with 4 passing tests and Ruff clean. It is not part of the bot feature plans; its `python -m zenkai_vault_mcp` module entrypoint is empty and no typechecker is configured.

Next required gate: finish and production-verify Plan 1, then begin Plan 2.



## 2026-09-25 Full Implementation Start

Status: in progress. The user selected implementation of all audited gaps across Plans 1–9. Work will proceed in plan order, with each plan verified before the next checkpoint.



## 2026-09-24 Complete Foundation Audit Verification

Status: Plan 1 remains in progress; no production/MVP release recommendation.

- Verification: bot `8 passed`, CLI help/version, Ruff, mypy, and `uv pip check`; MCP `4 passed` and Ruff.
- Reproduced: log messages can expose embedded credentials, empty health reports `operational`, invalid settings escape the structured startup error path, and the MCP module entrypoint exits without starting.
- Release blockers: unnecessary Message Content privileged intent, no capability-enforced dispatch, no Alembic/repository path, no truthful dependency health endpoint, no durable scheduler/event/audit wiring, and no Discord gateway `/ping` verification.
- Next gate: complete these Plan 1 controls with focused regression tests, then verify `/ping` in a staging guild before starting Plan 2.



## 2026-09-25 Deep Inspection Verification

Status: audit complete; implementation remains blocked at the Plan 1 acceptance gate.

Fresh checks passed: Bot 8 tests, Ruff, mypy, CLI help/version, uv dependency check, and database initialize/ping smoke. MCP 4 tests, Ruff, uv lock check, and a real stdio initialize plus vault_info handshake passed. No source files were modified.

Confirmed Plan 1 gaps remain: controlled configuration errors, secret-safe message/exception redaction, truthful empty health, consistent cache contract/TTL semantics, capability-enforced Discord dispatch, migrations/models/repositories, event/audit infrastructure, durable/recoverable production scheduler jobs, health endpoint, and Discord gateway/admin-denial verification. Plans 2–9 remain unimplemented. The checked task list above should not be interpreted as acceptance evidence; the later partial-audit table is the current status.


## 2026-09-25 Bot Bug Fix Start

Status: in progress. Investigating and fixing the confirmed Zenkai-Bot Plan 1 defects: secret-safe structured logging, controlled settings errors, truthful empty health, consistent cache TTL/JSON behavior, unnecessary Message Content intent, and capability-enforced Discord dispatch. Focused regression tests and all existing checks will be run before updating project memory.


## 2026-09-25 Plan 1 Bug Fixes Complete

Status: Plan 1 remains in progress. Fixed and regression-tested the confirmed bot control bugs: structured logging now redacts labeled, URL, raw authorization, exception, nested, and bytes credential forms without hiding ordinary words; invalid settings are logged through the startup path; empty health reports unavailable; cache Protocol, NullCache, and TTL behavior are consistent (`None` persists, `0` deletes, negatives fail); Message Content intent is disabled; command callbacks are capability-wrapped with ephemeral denial handling; partial startup and shutdown cleanup attempts all resources and preserves the primary failure.

Verification: 21 bot tests passed, Ruff passed, mypy passed across 16 source files, CLI help/version passed, database smoke passed, and `uv pip check` passed. Live Discord gateway `/ping` and staging admin-denial verification remain blocked until a valid token/guild is available. Plans 2–9 remain unimplemented.
