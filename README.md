---
tags: [zenkai, moc, discord-bot, index]
project: Zenkai
type: MOC
created: 2026-09-23
updated: 2026-09-24
---

# Zenkai — Discord Community Bot

Zenkai is a modular, Discord-native anime community bot. It combines AI assistance, anime and manga systems, member progression, moderation and raid protection, games, giveaways and events, support tickets, suggestions and bug reporting, notifications, analytics, server administration, and an optional web dashboard.

> **Core principle:** Maximum functionality with minimum unnecessary complexity.

## Documentation

All architecture, feature, and implementation documentation is consolidated into a single source of truth:

- **[Architecture, Features, and Implementation](Zenkai-Vault/02-Architecture/Zenkai-Architecture.md)**
- **[Execution Plan](Zenkai-Vault/01-Projects/Zenkai-Execution-Plan.md)**
- **[Bot Setup](Zenkai-Vault/04-Operations/Bot-Setup.md)**

The project memory and all project documentation live in the [`Zenkai-Vault/`](Zenkai-Vault/) Obsidian vault. The vault MCP is in [`Zenkai-MCP/`](Zenkai-MCP/).

The current implementation is the foundation phase with the core Discord runtime, configuration, logging, database, cache, scheduler, permissions, health registry, and `/ping` canary command.

## Feature Overview

| Area | Capabilities | Status |
| --- | --- | --- |
| AI | `/ask`, `/anime`, `/manga`, `/explain`, `/character`, `/summarize`, `/suggest`, `/bug`, `/pollai`, `/modai`, controlled mention-based chat | planned |
| Anime | search, recommendations, random, characters, watch-order, news feed | planned |
| Manga / Manhwa | search, recommendations, genre filtering, similar titles | planned |
| Community | profiles, XP, levels, badges, achievements, streaks, roles, welcome | planned |
| Moderation | warn, timeout, kick, ban, slowmode, logs, user history, raid protection | planned |
| Support | private tickets, categories, claiming, transcripts, inactivity auto-close | planned |
| Suggestions & Bugs | AI-structured suggestions, structured bug reports, staff-transitioned lifecycles | planned |
| Games | anime trivia, guess-the-character, Akinator style, random | planned |
| Entertainment | polls, `/pollai`, giveaways, events, watch parties, weekly/monthly awards | planned |
| Automation | notifications, reminders, status monitoring, news polling, scheduled jobs | planned |
| Analytics | member growth, activity, XP distribution, leaderboards | planned |
| Administration | optional dashboard, per-server configuration, custom commands, backups | planned |

## Repository Layout

```text
Zenkai/
├── Zenkai-Bot/       # Python Discord runtime, core infrastructure, features, and tests
├── Zenkai-MCP/       # Filesystem-backed Obsidian vault MCP server and tests
├── Zenkai-Vault/     # Obsidian project memory, architecture, plans, decisions, and operations
└── README.md         # Repository entry point
```

Each feature owns its commands, interactions, services, persistence rules, and scheduled jobs. Features depend on the shared core and provider interfaces — never on each other's internals.

## Obsidian Vault MCP

The project vault is `Zenkai-Vault/`. Its filesystem-backed MCP server lives in `Zenkai-MCP/` and exposes safe list/read/write/append/search/memory tools over stdio.

```bash
uv run --project Zenkai-MCP zenkai-vault-mcp
```

Use `Zenkai-MCP/config.example.json` as the MCP client configuration template. Set `ZENKAI_VAULT_PATH` to the absolute `Zenkai-Vault` path.

## Getting Started

See [Bot Setup](Zenkai-Vault/04-Operations/Bot-Setup.md) in the project vault.

```bash
cd Zenkai-Bot
cp .env.example .env
uv venv .venv
uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m zenkai
```

Requires Python 3.12+. SQLite is supported for local development; production deployments can use PostgreSQL 15+, Redis, and Node 20+ for the optional dashboard.

## Command Quick Reference

```text
/ask          General AI assistant
/anime        Anime assistant and search
/manga        Manga and manhwa assistant and search
/explain      Educational explanations (level: beginner|intermediate|advanced)
/character    Anime character information
/summarize    Summarize messages, threads, or authorized tickets
/suggest      AI-assisted suggestions
/bug          AI-assisted bug reporting
/pollai       Generate structured polls
/modai        AI-assisted moderation analysis (staff only)
/profile      Member profile card
```

## Development Phases

1. **Foundation** — Discord core, commands, database, configuration, permissions, logging, scheduler
2. **Community** — welcome, roles, XP, profiles, statistics
3. **Moderation & Support** — moderation, tickets, suggestions, bugs, backups
4. **AI** — AI tools, provider routing, controlled chat
5. **Anime** — anime, manga, news, awards
6. **Entertainment** — games, polls, giveaways, events, watch parties
7. **Automation** — notifications, status monitoring, scheduled jobs
8. **Dashboard & Ops** — admin panel, API, testing, deployment

See [Implementation Phases](Zenkai-Vault/02-Architecture/Zenkai-Architecture.md#43-implementation-phases) and [MVP](Zenkai-Vault/02-Architecture/Zenkai-Architecture.md#46-mvp) for the complete delivery plan.

## Design Principles

1. Discord-first and Discord-native.
2. Small core with independent, testable features.
3. Minimal dependencies and no unnecessary abstraction.
4. AI assists; authorized humans control consequential actions.
5. Time-based automation is deterministic and scheduler-driven.
6. Features are configured independently per Discord server.
7. External failures degrade one feature rather than taking down Zenkai.
8. Important actions are observable through structured, redacted logs and audit records.
9. Every production bug becomes a regression test.

See [Design Rules](Zenkai-Vault/02-Architecture/Zenkai-Architecture.md#48-design-rules) for the full list.