---
tags: [zenkai, project, active]
status: active
created: 2026-09-24
updated: 2026-09-24
---

# Zenkai Project

Zenkai is a modular, Discord-native anime community bot. The project combines AI assistance, anime and manga systems, member progression, moderation and raid protection, games, events, support tickets, notifications, analytics, administration, and an optional dashboard.

## Current State

- Foundation implementation is active in `../Zenkai-Bot/`.
- The foundation includes configuration, logging, errors, database access, cache, scheduler, permissions, health reporting, and a `/ping` canary command.
- The full delivery plan is in [[01-Projects/Zenkai-Execution-Plan]].
- The canonical feature and architecture reference is [[02-Architecture/Zenkai-Architecture]].

## Repository Map

| Path | Responsibility |
| --- | --- |
| `../Zenkai-Bot/` | Python bot runtime and tests |
| `../Zenkai-MCP/` | Obsidian vault MCP server and tests |
| `.` | This Obsidian vault |
| `../README.md` | Repository entry point |

## Delivery Order

1. Foundation
2. Community
3. Moderation and support
4. AI
5. Anime
6. Entertainment
7. Automation
8. Dashboard and operations
9. Hardening and release

## Definition of Done

A feature is complete only with implementation, Discord UX, permission checks, error handling, logging, required persistence, required scheduler integration, tests, and production verification. See [[02-Architecture/Zenkai-Architecture]].
