---
tags: [zenkai, architecture, implementation-plan, discord-bot]
created: 2026-09-23
updated: 2026-09-24
status: final
---

# Zenkai — Architecture, Features, and Implementation

Single comprehensive reference for Zenkai: a Discord-only anime community bot. It combines AI assistance, anime and manga systems, member progression, moderation and raid protection, games, giveaways and events, support tickets, suggestions and bug reporting, notifications, analytics, administration, and an optional web dashboard.

Zenkai is modular, Discord-native, and easy to debug. It aims for maximum useful functionality without unnecessary infrastructure or cross-feature coupling.

> **Core principle:** Maximum functionality with minimum unnecessary complexity.

## Contents

1. Project Definition
2. Platform Scope
3. High-Level Architecture
4. Repository Layout
5. Discord Interaction Model
6. Configuration
7. Database Schema
8. Permissions
9. Scheduler and Event System
10. Caching
11. External Providers
12. Logging and Audit
13. Error Handling
14. Observability
15. Live Status Monitoring
16. Backup System
17. Server-Specific AI Configuration
18. AI Tools
19. AI Provider Router and Safety
20. Anime
21. Manga and Manhwa
22. Anime News Feed
23. Anime Awards
24. Welcome and Leave
25. Roles
26. XP and Leveling
27. Profiles, Badges, and Achievements
28. Server Statistics
29. Moderation
30. Raid Protection
31. Tickets
32. Suggestions
33. Bug Reporting
34. Games
35. Polls
36. Giveaways
37. Events
38. Watch Parties
39. Notifications
40. Custom Commands
41. Admin Dashboard and Dashboard API
42. Testing Strategy
43. Implementation Phases
44. Installation and Operations
45. Troubleshooting
46. MVP
47. Definition of Done
48. Design Rules
49. Final Feature Map
50. Final Architecture Philosophy

## 1. Project Definition

Zenkai combines:

- AI assistance
- Anime and manga systems
- Member profiles and progression
- Moderation and raid protection
- Games
- Giveaways and events
- Advanced support tickets
- Suggestions and bug reporting
- Notifications
- Server analytics
- Server administration
- An optional web dashboard

Zenkai is a single coherent Discord community assistant, not 30 unrelated bots glued together.

## 2. Platform Scope

Zenkai is strictly Discord. It is a first-class Discord implementation rather than a Discord adapter inside a cross-platform framework.

### Supported

- Discord servers
- Discord channels and threads
- Discord roles and members
- Discord slash commands
- Buttons, select menus, and modals
- Embeds and permissions
- Scheduled and event workflows
- Webhooks where useful

### Out of Scope

- Telegram
- WhatsApp
- Slack
- Cross-platform gateway abstractions
- Telegram commands
- Generic multi-platform architecture

## 3. High-Level Architecture

```text
                         ZENKAI
                           │
             ┌─────────────┴─────────────┐
             │                           │
      Discord Gateway              Web Dashboard
             │                           │
             └─────────────┬─────────────┘
                           │
                      Zenkai Core
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
     Discord            Database             AI
     Runtime               │               Runtime
        │                  │                  │
        ▼                  ▼                  ▼
   Events/Commands     Members/Servers    Providers/Models
   Interactions        XP/Badges          Tools/Search
   Permissions         Tickets            Context
        │             Config
        └──────────────────┬──────────────────┘
                           │
                     Feature Modules
                           │
     ┌────────┬────────┬───┴───┬────────┬─────────┐
     ▼        ▼        ▼       ▼        ▼         ▼
   Anime    Games   Moderation Events Tickets   AI
     │        │        │       │        │         │
     └────────┴────────┴───────┴────────┴─────────┘
                           │
                    Notifications
                    Scheduler/Jobs
```

The user experience is:

```text
Discord
   ↓
Zenkai
   ↓
Simple interaction
   ↓
Correct specialized module
   ↓
Reliable result
```

## 4. Repository Layout

```text
zenkai/
├── core/
│   ├── discord/       # Gateway, interactions, commands, UX helpers
│   ├── database/      # Models, repositories, migrations, transactions
│   ├── permissions/   # Discord-backed authorization checks
│   ├── config/        # Server configuration, loading, validation
│   ├── scheduler/     # Shared durable scheduler and isolated jobs
│   ├── cache/         # Short-lived provider and configuration cache
│   └── logging/       # Structured logs, audit records, redaction
│
├── features/
│   ├── ai/
│   ├── anime/
│   ├── manga/
│   ├── members/
│   ├── leveling/
│   ├── moderation/
│   ├── tickets/
│   ├── suggestions/
│   ├── bugs/
│   ├── games/
│   ├── events/
│   ├── giveaways/
│   ├── notifications/
│   ├── watchparty/
│   ├── backup/
│   └── status/
│
├── dashboard/          # Optional administration dashboard
│
└── tests/
```

Each feature is independently understandable and testable. Large features may contain focused internal components:

```text
features/tickets/
├── service/
├── commands/
├── interactions/
├── permissions/
├── transcript/
├── scheduler/
└── tests/
```

Architectural boundaries:

- A feature owns its commands, interactions, services, persistence rules, and scheduled jobs.
- Core provides shared Discord, database, permissions, configuration, caching, scheduler, and logging infrastructure.
- Features call provider interfaces rather than external SDKs directly.
- Administrative operations always use the centralized permission layer.
- Time-based transitions are handled by deterministic jobs.
- AI output is advisory unless a user explicitly confirms a generated structure before it is posted.
- Dashboard features call the same domain services used by Discord interactions.
- No feature may directly mutate another feature's data. It must use an owning service, repository contract, or event.
- Secrets and credentials never enter logs, backups, generated content, or custom commands.
- Global utility classes that accumulate unrelated responsibilities are forbidden.

## 5. Discord Interaction Model

Zenkai uses Discord's native interaction system.

### Slash Commands

Slash commands handle explicit actions:

```text
/ask
/anime
/manga
/explain
/character
/summarize
/suggest
/bug
/modai
/pollai
```

### Buttons

Buttons support workflows such as:

```text
Create Ticket
Claim
Close
Reopen
Warn
Delete
Approve
Reject
Enter Giveaway
```

### Select Menus

Select menus support ticket categories, genres, games, configuration, role selection, and event options.

### Modals

Modals support ticket creation, bug reports, suggestions, events, polls, and configuration forms.

Prefix-style text commands are not part of the native interaction surface. Slash commands, buttons, context menus, and AI-driven tool calls all resolve to the same command handlers.

---

## Part I — Core Infrastructure

## 6. Configuration

Per-server configuration stored as key-value entries in `guild_config` plus feature flags in `guild_modules`.

### Principles

- Discord permissions remain the source of truth. Zenkai configuration can restrict, never expand, what Discord already allows.
- Every feature is independently enable/disable-able per server.
- Every configuration change is validated against a JSON schema, written through the owning feature or core service, recorded in `audit_logs`, and emitted as a `config.updated` event.
- User-facing strings and channel/role targets are configured per server, never hardcoded.

### Global Keys

- `locale`, `timezone` (UTC for storage; server timezone for display)
- `log_channel`
- `staff_roles[]`, `moderator_roles[]`, `support_roles[]`, `event_manager_roles[]`
- Feature default toggles applied to newly joined servers

### Editing

The dashboard writes to `PATCH /guilds/{id}/config` behind the dashboard authorization boundary. Discord-side configuration interactions are permitted only through the centralized permission layer.

Document new fields alongside implementation: JSON-schema, description, default value, and whether the value changes behavior immediately or on the next scheduler run.

## 7. Database Schema

PostgreSQL recommended (SQLite for development). Tables are prefixed `zenkai_` in production. Core entities stay small; activity beyond named entities uses audit and snapshot records.

### Core

```sql
guilds(id PK, name, locale, timezone, created_at)
guild_modules(guild_id FK, module TEXT, enabled BOOL, PK(guild_id, module))
guild_config(guild_id FK, key TEXT, value JSONB, updated_at, PK(guild_id, key))
users(id PK, discord_id UNIQUE, created_at)
guild_members(guild_id FK, user_id FK, joined_at, left_at, PK(guild_id, user_id))
audit_logs(id PK, guild_id FK, actor_id, action TEXT, feature TEXT, before JSONB, after JSONB, created_at)
```

### Members and Progression

```sql
member_stats(guild_id FK, user_id FK, messages INT, games_played INT, games_won INT,
             events_attended INT, giveaway_wins INT, last_active_at, PK(guild_id, user_id))
xp_ledger(id PK, guild_id FK, user_id FK, amount INT, reason TEXT, message_id, created_at)
xp_totals(guild_id FK, user_id FK, xp BIGINT, level INT, message_count INT, updated_at, PK(guild_id, user_id))
rank_defs(guild_id FK, level INT, title TEXT, role_id, PK(guild_id, level))
streaks(guild_id FK, user_id FK, kind TEXT, current INT, best INT, last_date DATE, PK(guild_id, user_id, kind))
achievements(id PK, guild_id FK, code, name, desc, icon, UNIQUE(guild_id, code))
user_achievements(guild_id FK, user_id FK, achievement_id FK, awarded_at, PK(guild_id, user_id, achievement_id))
badges(id PK, guild_id FK, code, name, desc, icon, UNIQUE(guild_id, code))
user_badges(guild_id FK, user_id FK, badge_id FK, awarded_at, PK(guild_id, user_id, badge_id))
```

Default level formula (configurable per server): `xp_for_level(n) = base * n ^ exponent` (`base=100`, `exponent=1.5`).

### Roles and Welcome

```sql
role_menus(id PK, guild_id FK, channel_id, message_id, type button|select|reaction, mode single|multi, config JSONB)
role_menu_items(menu_id FK, emoji_or_button_id, role_id, label)
autorole(guild_id PK, role_id, delay_sec, enabled)
welcome_config(guild_id PK, enabled, channel_id, card_template JSONB, message_template TEXT, dm_enabled, log_channel_id)
leave_config(guild_id PK, enabled, channel_id, message_template TEXT, farewell_enabled, log_channel_id)
```

### AI

```sql
ai_memory(guild_id FK, channel_id, user_id, role, content, created_at)
ai_tool_cache(guild_id FK, tool TEXT, query TEXT, payload JSONB, cached_at)
```

### Anime and Manga

```sql
anime_cache(source_id PK, kind anime|manga|character, payload JSONB, cached_at)
```

### Tickets

```sql
tickets(id PK, guild_id FK, user_id, category, thread_id, status, assignee_id, created_at, closed_at, closure_reason)
ticket_messages(id PK, ticket_id FK, message_id, author_id, content, attachment_urls JSONB, created_at)
ticket_transcripts(id PK, ticket_id FK, content JSONB, metadata JSONB, file_url, created_at)
```

### Suggestions and Bugs

```sql
suggestions(id PK, guild_id FK, author_id, title, description, motivation, implementation_hint, community_value,
            status, history JSONB, message_id, created_at)
bug_reports(id PK, guild_id FK, author_id, title, description, expected, actual, steps JSONB, environment JSONB,
            evidence JSONB, status, assignee_id, history JSONB, message_id, created_at)
```

### Entertainment

```sql
game_sessions(id PK, guild_id FK, channel_id, game TEXT, state JSONB, players JSONB, score JSONB, status, ends_at)
polls(id PK, guild_id FK, question, options JSONB, channel_id, message_id, anonymous BOOL, multi_vote BOOL, ends_at, status)
poll_votes(poll_id FK, user_id FK, option_idx, PK(poll_id, user_id))
award_defs(id PK, guild_id FK, code, name, desc, cadence weekly|monthly, criteria JSONB)
award_winners(id PK, award_id FK, user_id FK, period TEXT, decided_at)
giveaways(id PK, guild_id FK, channel_id, message_id, prize, winner_count, ends_at, requirements JSONB, status, winners JSONB, rerolls INT)
```

### Events and Watch Parties

```sql
events(id PK, guild_id FK, title, description, kind, channel_id, starts_at, ends_at, status, announcement_message_id, reminder_sent BOOL)
event_participants(event_id FK, user_id FK, status rsvp|attended|no_show, PK(event_id, user_id))
watch_parties(id PK, guild_id FK, anime_cache_source_id, episode, starts_at, channel_id, announcement_message_id, status, reminder_sent BOOL)
watch_party_participants(watch_party_id FK, user_id FK, rsvp BOOL, attended BOOL, PK(watch_party_id, user_id))
```

### Notifications, Custom Commands, Backups, Status, Stats

```sql
notifications(id PK, guild_id FK, channel_id, kind, source_ref, sent_at)
custom_commands(guild_id FK, name, response_type text|embed|action, response JSONB, permissions JSONB, cooldown_sec, PK(guild_id, name))
backups(id PK, guild_id FK, path, config_hash, created_by, created_at, restored_at JSONB)
service_status(source TEXT, status operational|degraded|unavailable, checked_at, metadata JSONB)
stat_snapshots(guild_id FK, kind, period, payload JSONB, created_at)
```

### Indexes

- `(guild_id, user_id)` on member stats, XP, streaks, suggestions, bugs, and tickets
- `ends_at` on giveaways, polls, game_sessions, events, and watch parties
- `created_at` on audit logs and activity tables
- GIN on `guild_config.value` when filtering is needed

### Migrations

Use Alembic and one migration per feature change. Seed default ranks, welcome configuration, and server-neutral feature defaults on guild join. Restore operations run inside a transaction and require explicit administrator authorization.

## 8. Permissions

One centralized permission layer gates every administrative operation.

### Capability Levels

```text
Owner
Admin
Moderator
Event Manager
Support
Member
```

### Sources of Truth

- Discord roles and hierarchy are the source of truth.
- Zenkai capability levels are mapped from server-configured Discord roles (`staff_roles[]`, `moderator_roles[]`, `support_roles[]`, `event_manager_roles[]`).
- Discord hierarchy checks still run server-side for every role assignment before role changes are attempted.
- No parallel permission universe is maintained beyond these server-mapped capabilities.

### Enforcement

- Command/action ACL: required capability, allowed channels, cooldown, and per-user rate limit
- Ticket checks: owner of own ticket, support staff on authorized tickets, moderators on report tickets, admins on all tickets
- Dashboard checks: Discord OAuth2 identity plus per-section ACL; the dashboard does not inherit Discord command permissions
- AI: advisory only — AI alerts never bypass permission checks; AI never performs administrative or moderation actions

### Denials

- Denied interactions reply ephemerally with a clear message.
- Denied actions and suspicious denials are written to the audit log where configured.
- One shared error type renders the same denial UX everywhere.

## 9. Scheduler and Event System

One shared scheduler and event bus underneath every feature. No feature runs its own background worker or loop.

### Rules

- Deterministic automation: time-based transitions (expiries, reminders, closings, endings) are decided by the scheduler, not by AI. AI may classify and log; the scheduler enforces configured timeouts.
- Isolated jobs: one failing job interrupts its own retries without blocking unrelated jobs.
- Idempotent handlers: re-runs after restart must not double-award or double-notify.
- UTC everywhere internally; server timezone only for display.
- Jitter for large fan-out; bounded retries with backoff for external calls.
- Audit rows and bus events on every important side effect.

### Event Bus Topics

- `message.created`, `member.joined`, `member.left`
- `xp.gained`, `level.up`
- `streak.updated`
- `poll.ended`
- `giveaway.ended`
- `award.due`, `award.decided`
- `suggestion.transition`
- `bug.transition`
- `ticket.created`, `ticket.claimed`, `ticket.closed`, `ticket.auto_closed`, `ticket.reopened`
- `event.created`, `event.reminder`, `watchparty.reminder`
- `moderation.action`
- `ai.moderation.alert`
- `notification.sent`
- `config.updated`
- `maintenance.announce`
- `backup.created`
- `service.status_changed`

### Scheduler Jobs

| Job | Cadence | Owner |
| --- | --- | ----- |
| giveaways.ender | every 30s | giveaways |
| polls.ender + recurring poll creator | every 30s / cron | polls |
| awards.evaluator (weekly/monthly) | cron, per server | awards |
| tickets.inactivity (reminder then grace then auto-close) | every 60s | tickets |
| events.reminders | every 60s | events |
| watchparty.reminders | every 60s | watchparty |
| streaks.reset / daily roll | cron daily | leveling |
| news.poll | cron per server | anime |
| ai.memory summary + TTL cleanup | hourly | ai |
| status.monitor (retry then confirm then notify) | every 5m | status |
| stats.rollup | hourly/daily | statistics |
| backups.scheduled | cron per server | backup |
| updates.announce | one-shot / cron | notifications |
| anime cache pruner | daily | anime |

### Job Definition

```python
JobDefinition(
    id="tickets.inactivity",
    cron_or_interval="* * * * *",
    handler=tickets.check_inactive,
    idempotent=True,
    per_guild=True,
)
```

### Recovery

- Jobs and their run metadata must survive restarts.
- Missed one-shot reminders are evaluated on startup against their deadlines.
- Health checks surface missed schedules through the observability layer.

## 10. Caching

Zenkai may cache:

- Anime metadata
- Character metadata
- Server configuration
- Member profile data where appropriate

Use bounded expiration and invalidation. The cache reduces API use and latency but never becomes an unreconciled second database. Stale or missing cache entries trigger a fetch rather than serving fabricated data.

## 11. External Providers

External integrations use small interfaces:

```text
AnimeProvider
MangaProvider
AIProvider
NewsProvider
StatusProvider
```

Feature code depends on the interface rather than a specific external API:

```text
/anime
  ↓
AnimeService
  ↓
AnimeProvider
  ↓
Current API
```

Provider replacement should require changes only in the provider integration and its tests. Provider-specific code must never leak into AI features or any other feature.

## 12. Logging and Audit

Every important action creates a structured record. Event names include:

```text
MEMBER_JOINED
MEMBER_LEFT
ROLE_ASSIGNED
MODERATION_ACTION
TICKET_CREATED
TICKET_CLAIMED
TICKET_CLOSED
TICKET_AUTO_CLOSED
SUGGESTION_CREATED
BUG_CREATED
EVENT_CREATED
GIVEAWAY_CREATED
GIVEAWAY_COMPLETED
CONFIG_CHANGED
BACKUP_CREATED
AI_MODERATION_ALERT
```

Logs must support diagnosis without exposing secrets, producing unbounded message dumps, or creating unstructured walls of text.

## 13. Error Handling

Every external dependency has:

- Timeout
- Bounded retry
- Fallback where available
- Clear user-facing error
- Structured internal logging

A user-facing provider failure may read:

> Zenkai couldn't reach the anime database right now. Please try again shortly.

Technical exception details remain in redacted internal logs. One external dependency failure degrades one feature rather than taking down Zenkai.

## 14. Observability

Monitor:

- Discord gateway status
- Command latency
- External API latency
- AI latency
- Error rate
- Rate limits
- Database health
- Scheduler health
- Memory usage
- Background job failures

Provide a basic health and status endpoint for the dashboard or deployment environment.

## 15. Live Status Monitoring

Monitor external services and internal subsystems Zenkai depends on, with retry and confirmation logic before alerting.

### Monitored

- Discord Gateway
- Database
- Scheduler health
- AI provider(s)
- Anime/manga provider
- Redis (when used)
- Optional external endpoints from `STATUS_ENDPOINTS`

### Statuses

```text
Operational
Degraded
Unavailable
```

### Alerting

```text
Service failure
      ↓
Retry (bounded, with backoff)
      ↓
Confirm failure
      ↓
Discord notification (status channel)
      ↓
Recovery notification when restored
```

Transient one-off failures never produce alerts. Confirmation requires consecutive failures across retries.

### Configuration

- `status.enabled`, `status.channel_id`
- `status.check_interval_sec`, `status.retries_before_alert`
- `status.alert_role`
- `status.endpoints[]` (method, URL, expected status)

Downtime and recovery events emit `service.status_changed` and feed notifications.

## 16. Backup System

Backup Zenkai configuration for consistent server re-provisioning. Backups are configuration snapshots, never credential dumps.

### Included

- Role and channel configuration
- Server settings and feature configuration
- Custom commands
- Ticket configuration (not ticket transcript contents)
- Level and rank definitions
- Notification configuration
- Server-specific feature settings

### Explicitly Excluded

- Discord tokens and OAuth credentials
- API keys
- Any secret stored in environment configuration

### Workflow

```text
Scheduled backup
   ↓
Collect configuration objects
   ↓
Strip and validate secrets
   ↓
Hash payload
   ↓
Write backup + audit record
```

Restoration:

```text
Administrator authorizes restore
   ↓
Preview of changes
   ↓
Restore applies inside a transaction
   ↓
Validate configuration
   ↓
Audit record
   ↓
config.updated events
```

### Configuration

- `backup.enabled`, `backup.location`
- `backup.schedule_cron`
- `backup.retention_count`
- `backup.restore_requires_admin`

### Safety

- Restore requires explicit administrator authorization; there is no unattended restore.
- A restore preview lists changed keys before commit.
- A failed validation rolls back the transaction.
- Backups are write-only from runtime scope; restore reads are operator-initiated.

---

## Part II — AI

## 17. Server-Specific AI Configuration

Zenkai behaves per server while sharing one codebase. Configuration lives in `guild_config` keys `ai.*` and `personality.*`. Changes are validated, audited, and reflected in the system prompt for the next request.

### Personality

```text
Bot Personality
├── Name
├── Tone (friendly|formal|playful|tsundere|stoic...)
├── Greeting style
├── Emoji style (none|sparse|anime-spam)
├── Anime theme (e.g. Naruto, One Piece, generic)
├── Response length (short|medium|detailed)
├── Humor level (0-10)
├── Moderation sensitivity (0-10)
└── Custom system instructions (free text, token-limited)
```

`moderation_sensitivity` only changes what the AI flags for staff review. It never changes what the bot can enforce autonomously.

### Server Controls

- `ai.enabled`
- `ai.channel_allowlist[]` / `ai.channel_denylist[]`
- `ai.enabled_commands[]`
- `ai.response_length`, `ai.personality_profile`
- `ai.provider`, `ai.model` with eligible fallbacks
- `ai.cooldown_sec_per_user`

### System Prompt Builder

```text
base safety + personality + server rules + channel context
```

Cap custom instructions (for example ~800 characters) so the safety boundary cannot be overwhelmed by server-defined text.

## 18. AI Tools

Zenkai's AI is a specialized collection of tools, not one unrestricted assistant.

### `/ask`

General assistant: questions, explanations, casual conversation, reasoning, and approved server-aware context.

### `/anime`

Anime information, recommendations, genre discovery, similar anime, watch-order questions, character relationships, and discussion.

### `/manga`

Manga and manhwa recommendations, genre filtering, similar works, reading suggestions, and basic information.

### `/explain`

Educational assistant with `level: beginner|intermediate|advanced`. Prioritizes clarity over unnecessary technical language.

### `/character`

Character information, personality, abilities, relationships, series, similar characters, and recommendations.

### `/summarize`

Summarizes selected messages, threads, long discussions, or authorized ticket conversations. Output: summary, key points, decisions, open issues, action items. Private content requires a permission check before summarization.

### `/suggest`

AI structures a suggestion into title, description, motivation, possible implementation, and community value, then posts it to the suggestions channel for voting and staff review. The user confirms the structured output before the post is created.

### `/bug`

AI asks for missing information and organizes a bug report (title, description, expected, actual, steps, environment, evidence). It never invents missing facts or claims fixes.

### `/pollai`

Generates a question and options; the server confirms the generated structure before Discord creates the poll.

### `/modai`

Flags potentially toxic messages, harassment, spam, and suspicious patterns for staff review. AI only provides evidence and context; staff choose to ignore, warn, delete, escalate, or investigate. AI never punishes a user and never bans anyone.

### Normal Chat

Controlled activation only via bot mention, a reply to Zenkai, an explicit AI interaction, or a configured AI-enabled channel. Every-message AI responses are not implemented.

### Pipeline

```text
Discord Message
      ↓
Activation + Classification
      ↓
Context + Memory
      ↓
Provider Router
      ↓
Response Validation
      ↓
Discord Response
```

Classification keeps factual, command, game, and moderation routes separate.

### Context and Memory

- Short-term: last N message context per channel/thread.
- Long-term: `ai_memory` summaries per user/server with TTL and an hourly summarizer job.
- Personality injection per section 17.

### Configuration

- `ai.enabled`, `ai.channel_allowlist[]`/`denylist[]`, `ai.enabled_commands[]`
- `ai.provider`, `ai.model`, `ai.max_tokens`, `ai.temperature`
- `ai.memory_window`, `ai.fact_check_enabled`, `ai.web_search_enabled`
- `ai.cooldown_sec_per_user`, `ai.cost_cap_per_period`

## 19. AI Provider Router and Safety

### Router

Selects among providers based on availability, rate limits, task requirements, cost, latency, and capability. On failure or rate limit, it tries the next eligible provider.

```text
Request
 ↓
Provider A
 ↓
Failure/rate limit
 ↓
Provider B
 ↓
Response
```

Model heat, cost caps, and per-user cooldowns are enforced before requests are dispatched.

### Validation and Safety

- Respect moderation sensitivity without autonomous action.
- Hallucination guard: factual anime/manga answers without a tool result are hedged and point to `/anime`, `/manga`, or `/character`.
- PII, invite, and raid patterns are suppressed and logged.
- Length, emoji, humor, and tone follow server personality.
- AI cannot ban, delete servers, change permissions, grant the administrator role, or apply moderation punishment.

### AI Assistance in Moderation

```text
Message
   ↓
AI analysis
   ↓
Potential violation?
   ↓
Staff alert with evidence
   ↓
Moderator decision
```

AI provides evidence and context, not final authority.

---

## Part III — Anime and Manga

## 20. Anime

Anime-focused functionality routes through an `AnimeService` talking to an `AnimeProvider` interface; feature code depends on the interface, not the external API.

### Commands

- `/anime <name>` — information, genres, status, episodes, rating/source data
- `/anime random` — random anime
- `/anime similar <name>` — similar works
- `/character <name>` — character information
- `/manga <name>` — manga and manhwa information

### Capabilities

- Anime information and search
- Recommendations and genre discovery
- Similar anime
- Watch-order questions where reliable data is available
- Character information, relationships, and recommendations
- Anime news feed

Zenkai never invents facts. If the provider returns no result, the response says unknown rather than inventing details.

### Cache

`anime_cache(source_id, kind anime|character, payload, cached_at)` with expiration.

### Configuration

- `anime.enabled`
- `anime.provider`, `anime.cache_ttl_hours`
- `anime.nsfw_filter`
- `anime.news_sources[]`, `anime.news_channel_id`, `anime.news_frequency`, `anime.news_filters{}`

## 21. Manga and Manhwa

Manga/manhwa functionality remains separate from anime internally even when providers are shared. `/manga` routes through `MangaService` → `MangaProvider`.

### Commands

- `/manga <name>` — manga/manhwa information
- `/manga random` — random title
- `/manga similar <name>` — similar works
- `/manga genre <genre>` — genre-filtered recommendations

### Facts

- Never invent volumes, chapters, release dates, or statuses; provider misses return "unknown".
- Caching may share `anime_cache` kinds, but manga data is validated under the manga schema.

### Configuration

- `manga.enabled`
- `manga.provider`, `manga.cache_ttl_hours`
- `manga.nsfw_filter`
- `manga.genre_result_limit`

## 22. Anime News Feed

Administrators configure news sources, genres, channels, posting frequency, and filters. The news polling scheduler job runs per server.

Each post includes title, source, image when available, short summary, and link. Duplicate reposts are suppressed via a content hash per source.

## 23. Anime Awards

Weekly and monthly community awards. The community votes through Discord interactions; the scheduler closes voting at the configured boundary.

### Categories

- Anime of the Week
- Character of the Week
- Opening of the Week
- Best Fight
- Best Episode

### Data

- `award_defs(code, name, desc, cadence, criteria JSONB)`
- `award_winners(id, award_id, user_id, period, decided_at)`

### Workflow

1. Create or schedule award definitions.
2. Announce voting with a Discord interaction.
3. Close votes on the `awards.evaluator` scheduler job.
4. Record winners and announce results.
5. Award badges/XP and update profiles.

### Configuration

- `awards.enabled`, `awards.channel_id`
- `awards.weekly_day`, `awards.monthly_day`
- `awards.rewards{}`, `awards.categories[]`

Winner selection and tie-breaking are deterministic and unit-tested; storage is UTC.

---

## Part IV — Community

## 24. Welcome and Leave

Server-configurable welcome and leave messages with card rendering (avatar, name, member count, server banner, anime theme).

### Welcome

- Message templates with variables: `{user}`, `{server}`, `{count}`, `{rules_channel}`
- Custom card: background, accent, font
- Optional DM welcome
- Optional leave/farewell message
- Join and leave logs in the configured log channel

### Flow

```text
member.joined
    ↓
Configured auto-roles (with hierarchy check)
    ↓
Render welcome card
    ↓
Send to welcome channel (+ optional DM)
    ↓
Join log
    ↓
Statistics increment
```

### Configuration

- `welcome.enabled`, `welcome.channel_id`
- `welcome.card_template {bg, font, accent}`, `welcome.message_template`
- `welcome.dm_enabled`, `welcome.dm_template`
- `welcome.log_channel`
- `leave.enabled`, `leave.channel_id`, `leave.message_template`, `leave.farewell_enabled`, `leave.log_channel`

Card rendering is offloaded with timeouts; failures never block member joins.

## 25. Roles

Slash commands and button/select role menus manage role assignment. Discord is the source of truth for hierarchy and permissions.

### Types

- Button-determined role menus
- Select-menu role menus
- Reaction roles (legacy Discord flows)
- Auto-roles assigned on member join
- Level/XP reward roles assigned on `level.up`
- Internal permission roles for staff, support, event managers, and admins

### Design

- One message → many roles; menu mode `single` (exclusive) or `multi`
- Requirements: minimum level, account age, not-muted, not-blacklisted
- Auto-role on join with optional delay
- Level reward roles integrate with the XP system

### Configuration

- `roles.max_per_user`
- `roles.menu_cooldown`
- `roles.autorole_role`, `roles.autorole_delay_sec`
- `roles.log_channel`

### Safety

- Verify `manage_roles` and role hierarchy before every assignment or removal. The highest Zenkai-assigned role must sit above target roles.
- Every assignment/removal is written to the audit log.
- Menu clicks are rate-limited.
- Failed assignments produce a clear error and an audit entry, not silent retries.

## 26. XP and Leveling

Event-driven progression with explicit anti-abuse controls.

```text
Message / activity event
    ↓
Anti-spam / cooldown / daily-limit checks
    ↓
XP calculation
    ↓
Level calculation
    ↓
Reward check (roles, badges, cosmetics)
    ↓
Achievement / streak check
    ↓
Leaderboard update
```

### Rules

- Cooldown 45–60s per user by default; minimum message length; no XP for commands, buttons, or bot messages.
- Duplicate and rapid-fire messages award zero.
- Daily caps and suspicious farming detection (bulk gain in short windows, repeated cycling) are enforced and audited.
- Formula: `gain = rand(min, max) * boosters` with channel multipliers, role boosters, and weekend multipliers.
- Level formula: `xp_for_level(n) = base * n^exponent`. Ranks are server-configurable, never hardcoded.
- Reward check assigns ranks on `level.up` through the roles system.
- Achievements include first message, 7-day and longer streaks, message counts, event/game wins.

### Streaks

- Daily activity, chat, events, and optional anime-related activity streaks.
- Streak updates are event-driven; streak resets run on the daily scheduler job.
- Streaks must not reward spam.

### Leaderboards and Resets

- `xp_totals` plus cached daily/weekly/monthly views.
- Optional seasonal reset uses the scheduler, with announcement and export before resetting.

### Configuration

- `xp.enabled`, `xp.cooldown_sec`, `xp.min_gain`, `xp.max_gain`
- `xp.formula_base`, `xp.formula_exponent`
- `xp.channel_multipliers{}`, `xp.role_boosters{}`, `xp.weekend_multiplier`
- `xp.excluded_channels[]`, `xp.excluded_roles[]`, `xp.daily_cap`
- `xp.role_rewards_enabled`, `xp.announce_level_up`, `xp.levelup_channel`

### Edge Cases

- Bulk XP exploits are rate-limited and audited; suspected farming is alerted, not silently granted.
- The bot role must sit above every reward role in the Discord hierarchy.
- Imports and backfills use a distinct `reason='import'` so they cannot double-trigger rewards.
- Leveling down is only possible through an explicit, audited reset.

## 27. Profiles, Badges, and Achievements

`/profile [@user]` renders a member card with:

- XP, level, rank title
- Badges and achievements
- Streaks
- Message/activity statistics
- Game statistics (wins, losses, win rate, high score)
- Event participation
- Award wins
- Anime and manga preferences when privacy allows

### Sources

`xp_totals`, `user_achievements`, `user_badges`, `streaks`, `member_stats`, game session rollups, `award_winners`, and `stat_snapshots`.

### Badges and Achievements

Achievements are event-driven and stored once per server:

- Anime Veteran, Game Master, Streak Warrior, Event Champion, Community Member, Trivia Master, Giveaway Winner, Early Member, plus server-defined codes.

Badges and achievements are awarded through one service so duplicates are impossible and awarding is auditable.

### Privacy

- `profiles.public_by_default` with a user opt-out flag.
- Anime preferences stored only when the user opts in.
- Profile data is never included in AI context without explicit authorization.

Card rendering shares infrastructure with welcome cards; failures degrade to a fallback embed.

## 28. Server Statistics

Rolled-up, privacy-conscious analytics for server insights and dashboard charts.

### Tracked

- Member count and member growth (net joins/leaves)
- Active members and activity (messages per hour/day, active users)
- XP and level distribution
- XP gained per period
- Game activity and win rates
- Poll and event participation
- Leaderboard snapshots (XP, messages, games, helpfulness, streaks)

### Storage and Consumption

Rollup jobs write `stat_snapshots(guild_id, kind, period, payload JSONB, created_at)` hourly/daily. Leaderboards are cached and paginated embeds in Discord; dashboard charts read the same snapshots through the API. Per-server retention limits bound storage growth.

---

## Part V — Moderation and Support

## 29. Moderation

Explicit moderator tools with a centralized permission layer. Discord permissions remain the source of truth; Zenkai configuration can restrict further, never expand.

### Actions

- Warn
- Timeout
- Kick
- Ban
- Message deletion
- Lock channel
- Slowmode
- Moderation logs
- User history

Every action requires a reason, requires the moderator capability, respects the target hierarchy, and writes an audit record.

### Workflow

```text
Moderator action request
    ↓
Permission check (moderator/admin)
    ↓
Discord hierarchy + bot position check
    ↓
Execute
    ↓
Audit log + optional log channel + bus event
```

### User History

- A per-user record aggregates warnings, timeouts, kicks, bans, tickets, and AI alerts per server.
- Staff can review history before acting.
- History is private to staff and never exposed through public profiles.

### Configuration

- `moderation.enabled`, `moderation.log_channel`
- `moderation.actions_allowed[]`
- `moderation.default_timeout_sec`
- `moderation.raid.join_spike`, `moderation.raid.new_account_age`, `moderation.raid.alert_role`
- `moderation.raid.protection_actions[]`

## 30. Raid Protection

Detect unusual activity such as join spikes, new-account influx, repeated suspicious patterns, spam waves, and suspicious message activity.

Response flow:

```text
Normal → Monitor

Suspicious → Alert staff

Severe spike → Enable configured protection and notify staff
```

Configured protection may include slowmode, channel lock, or join verification. Users are never banned solely from an AI classification.

## 31. Tickets

Advanced private support channels with categories, claiming, staff assignment, transcripts, and deterministic inactivity automation.

### Creation

```text
Create Ticket button
   ↓
Select category (Support / Bug / Report / Suggestion / Other)
   ↓
Private channel + opening embed + controls
```

### Permissions

- Member: own ticket
- Support staff: assigned/authorized tickets
- Moderator: reports and moderation tickets per server config
- Admin: all tickets

### Controls

Every ticket has: Claim, Add Staff, Lock, Reopen, Close. Claim updates state and assignment.

### State Machine

```text
OPEN
 ↓
CLAIMED
 ↓
WAITING
 ↓
RESOLVED
 ↓
CLOSED

CLOSED → OPEN (reopen)
```

Invalid transitions are rejected and logged.

### Transcript and Closure

```text
Ticket
 ↓
Generate transcript
 ↓
Save metadata
 ↓
Closure log
 ↓
Archive / delete channel
```

Transcript metadata: ticket ID, user, category, staff member, created/closed times, duration, messages, attachments/links where available, and closure reason. Closure reason is required; staff member and source (`manual` or `auto_close`) are recorded.

### Inactivity Automation

```text
No activity
   ↓
Scheduler detects inactivity
   ↓
Reminder
   ↓
Grace period
   ↓
Auto-close
```

AI may classify whether a ticket looks resolved or waiting on the user, but the scheduler decides when the configured timeout expires.

### Configuration

- `tickets.enabled`, `tickets.category_codes[]`
- `tickets.allowed_role` / `tickets.support_roles[]`
- `tickets.inactive_after_sec`, `tickets.grace_sec`, `tickets.auto_close_enabled`
- `tickets.transcript_channel`
- `tickets.max_open_per_user`

## 32. Suggestions

Members submit ideas (server ideas, bot features, community improvements, event ideas) through `/suggest`, a modal, or a button. Each item gets an ID and a full audit history.

### AI-Assisted Submission

```text
User idea
   ↓
AI asks for missing information
   ↓
AI structures the suggestion
   ↓
Title / Description / Motivation / Implementation / Value
   ↓
User confirms
   ↓
Post to suggestions channel
```

### Lifecycle

```text
SUBMITTED
    ↓
UNDER_REVIEW
    ↓
PLANNED / REJECTED
    ↓
IMPLEMENTED / COMPLETED
```

Transitions emit `suggestion.transition` events; the author is notified and the transition is audited. Community voting uses Discord interactions; only staff with the configured capability may transition status.

### Configuration

- `suggestions.enabled`, `suggestions.channel_id`
- `suggestions.staff_role`
- `suggestions.auto_thread`
- `suggestions.kinds[]`

## 33. Bug Reporting

Dedicated structured bug reports with a clear lifecycle. `/bug` opens the flow; AI assists with organization, never with invention.

### Submission

```text
User describes problem
        ↓
AI asks for missing information
        ↓
AI organizes known details
        ↓
Bug Report
├── Title
├── Description
├── Expected behavior
├── Actual behavior
├── Reproduction steps
├── Environment
└── Evidence
        ↓
Posted to bug-report channel
```

Evidence includes message links, screenshots, or command output when provided. Missing details are requested, never fabricated.

### Statuses

```text
OPEN
INVESTIGATING
CONFIRMED
IN PROGRESS
FIXED
CLOSED
```

Only staff with the `bugs.reviewer` capability can transition status. `FIXED` requires verified evidence; AI never marks a report fixed. Similar open reports are surfaced before new submissions are promoted.

### Configuration

- `bugs.enabled`, `bugs.channel_id`
- `bugs.reviewer_role`
- `bugs.auto_notify_author`

---

## Part VI — Entertainment

## 34. Games

Games run inside one common session engine and are distinct from the AI and anime command surfaces.

```text
GameSession
├── game_id
├── channel_id
├── players
├── state
├── question
├── score
├── timeout
└── result
```

States: `lobby → active → answered/timeout → finished`.

### Initial Games

- **Anime Trivia** — questions → answers → score
- **Guess the Character** — clues, cropped image, silhouette, or description
- **Akinator-style** — progressive questions narrowing a character
- **Random anime/character** — lightweight entertainment command

New games subclass `GamePlugin` (`start`, `on_answer`, `on_timeout`, `score`).

### Statistics

The engine records games played, wins, losses, high score, and win rate. Per-player statistics feed profiles, statistics, and reward logic via bus events.

### Configuration

- `games.enabled`, `games.allowed[]`
- `games.timeout_sec`
- `games.max_concurrent_per_channel`
- `games.xp_reward_win/participate`
- `games.cooldown_sec`

Scheduling is deterministic and timeout-driven; no game feature runs its own background loop.

## 35. Polls

Custom and recurring polls through Discord interactions.

### Custom Polls

- Question with up to 10 options
- Buttons for voting
- Duration with scheduler-driven closure
- Anonymous and multi-vote flags where server policy permits
- `poll.ended` event → results embed

### AI-Generated Polls

`/pollai topic:"Best Naruto arc"` produces a question plus 2–4 options, confirmed by the server before creating the Discord poll.

### Recurring Polls

Weekly/monthly cadence via cron; templates snapshot options each run.

### Configuration

- `polls.enabled`, `polls.default_duration_h`
- `polls.max_options`, `polls.allow_recurring`
- `polls.anonymous_by_default`, `polls.multi_vote_by_default`
- `polls.results_channel`

## 36. Giveaways

Timed giveaways with an entry button, deterministic winner selection, rerolls, eligibility requirements, and complete logging.

### Workflow

```text
Create giveaway (prize, duration, win count, requirements)
   ↓
Announce with Enter button
   ↓
Scheduler checks expiry
   ↓
Reroll / select winner(s)
   ↓
Announce winners
   ↓
DM + award
```

The `giveaways.ender` job runs every 30 seconds in UTC.

### Eligibility

- Minimum level / role / account age
- Not-muted and not-blacklisted
- Bonus entries for configured activities (max capped)

### Rules

- Winner selection is deterministic (seeded from the draw window).
- Reroll is staff-only, audited, and recorded in `giveaways.rerolls`.
- `giveaway.ended` events feed notifications and stats.

### Configuration

- `giveaways.enabled`, `giveaways.default_duration_h`
- `giveaways.log_channel`, `giveaways.max_concurrent`
- `giveaways.eligibility_defaults{}`

## 37. Events

Community events: trivia nights, community events, tournaments, awards, and watch-party-driven sessions.

### Capabilities

- Event creation with title, description, kind, channel, start/end times
- Announcement embed
- Reminders before start
- RSVP/attendance buttons
- Participant tracking
- Event results and history

### Workflow

```text
Create event
   ↓
Announcement
   ↓
RSVP closes / starts
   ↓
Reminders (scheduled)
   ↓
Event
   ↓
Attendance tracking
```

### Configuration

- `events.enabled`, `events.announce_channel`
- `events.rsvp_enabled`, `events.reminder_lead_minutes[]`
- `events.max_participants`
- `events.default_kind`

RSVP status: `rsvp | attended | no_show`. Attendees can earn XP and event participation counters.

## 38. Watch Parties

Dedicated anime watch-party workflow for coordinated viewing sessions.

### Workflow

```text
Create Watch Party
        ↓
Anime / episode / date-time
        ↓
Announcement
        ↓
RSVP
        ↓
Reminder
        ↓
Event
        ↓
Attendance tracking
```

Anime and episode references come from validated provider data, never an assumed episode counter.

### Configuration

- `watchparty.enabled`, `watchparty.channel_id`
- `watchparty.reminder_lead_minutes[]`
- `watchparty.max_participants`
- `watchparty.attendance_tracking_enabled`

---

## Part VII — Automation and Administration

## 39. Notifications

Configurable per-server, per-channel notifications routed through one owned service so quiet-hours, cooldowns, and audit logging are consistent.

### Types

- Bot updates, changelogs, releases
- Service status and downtime
- Anime news
- Event and watch-party reminders
- Ticket inactivity reminders
- Giveaway endings
- Scheduled announcements

### Schedule

- One-shot and repeating announcements are scheduler jobs.
- Reminders are sent before deadline, not looping messages.

### Configuration

- `notifications.enabled`, `notifications.channel_id`
- `notifications.ping_role`
- `notifications.cooldown_per_channel`
- Per-kind flags: `updates.*`, `status.*`, `events.*`, `tickets.*`, `giveaways.*`

Role pings never exceed the permission check for the sender. Failed service notifications are retried with backoff, not re-emitted by every listener.

## 40. Custom Commands

Per-server slash commands defined by administrators. Slash commands are canonical.

### Definition

- `custom_commands(guild_id, name, response_type text|embed|action, response JSONB, permissions, cooldown)`
- Aliases resolve to the same handler.
- Response may include text, embeds, images, and buttons.
- Variables: `{user}`, `{level}`, `{count}`, `{server}`.

### Behavior

```text
Command Definition
   ↓
Permission Check
   ↓
Argument Validation
   ↓
Handler
   ↓
Response
```

No custom command can execute arbitrary code; responses are constructed from defined variables and allowed embed types only. Created and edited through the dashboard and staff-only commands; changes are validated, audited, and applied immediately.

### Configuration

- `commands.enabled`
- `commands.global_cooldown_sec`
- `commands.max_custom_commands`

## 41. Admin Dashboard and Dashboard API

Optional web dashboard. It configures Zenkai and surfaces analytics; it does not duplicate Discord workflows.

### Sections

```text
Dashboard
├── Overview (health, member count, activity, active giveaways/polls)
├── Members
├── Moderation
├── Tickets
├── AI
├── Anime
├── Leveling
├── Games
├── Events
├── Giveaways
├── Notifications
├── Custom Commands
├── Backups
└── Server Settings
```

### Authorization

- Discord OAuth2 identity plus guild membership.
- `manage_guild` or server-mapped dashboard capability required.
- Per-section ACL enforced server-side.

### Write Flow

```text
Dashboard save
   ↓
PATCH /guilds/{id}/config (validated)
   ↓
JSON-schema validation
   ↓
Write guild_config / domain service
   ↓
audit_logs insert
   ↓
config.updated bus event
```

Module toggles write `guild_modules` live. Backups and restores are guarded by explicit authorization.

### API Endpoints

- `GET /guilds` — servers the caller may administer
- `GET/PATCH /guilds/{id}/config` — validated, audited configuration writes
- `GET/PUT /guilds/{id}/modules` — feature enable/disable
- `GET /guilds/{id}/stats?kind=&period=` — analytics snapshots
- `GET /guilds/{id}/leaderboard?type=xp|games|streaks&range=`
- `GET /guilds/{id}/members` — active members and profiles
- `GET/POST /guilds/{id}/tickets`, `POST /guilds/{id}/tickets/{id}/claim|reopen|close`
- `GET/POST /guilds/{id}/suggestions`, `POST .../{id}/transition`
- `GET/POST /guilds/{id}/bugs`, `POST .../{id}/transition`
- `GET/POST /guilds/{id}/giveaways`, `POST .../{id}/reroll`
- `GET/POST /guilds/{id}/polls`, `POST .../{id}/close`
- `GET/POST /guilds/{id}/events`, `POST .../{id}/remind`
- `GET/POST /guilds/{id}/watchparties`
- `GET/POST /guilds/{id}/notifications`
- `GET/POST /guilds/{id}/custom-commands`
- `GET/POST /guilds/{id}/backups`, `POST /guilds/{id}/backups/{id}/restore`
- `GET /guilds/{id}/ranks`, `GET /guilds/{id}/audit`
- `GET /health` — gateway, database, Redis, scheduler, AI provider, anime provider status

### WebSocket

`WS /ws/guilds/{id}` emits `config.updated`, `giveaway.ended`, `suggestion.transition`, `bug.transition`, `ticket.status_changed`, `level.up`, `notification.sent`, and `service.status_changed`.

### Conventions

- All writes go through the same domain services the Discord gateway uses.
- All writes validate schemas, write audit records, and emit `config.updated` events.
- Provider and credential configuration is never returned by the API.
- Restore endpoints require explicit administrator authorization and run inside a transaction.

---

## Part VIII — Delivery

## 42. Testing Strategy

Every feature requires tests before it is considered complete.

### Unit Tests

Cover:

- XP and level calculation
- Ticket state transitions
- Permission checks
- Giveaway winner logic
- Streak logic
- Poll generation
- Provider router fallback ordering

### Integration Tests

Cover:

- Discord interactions
- Database repositories and transactions
- Scheduler jobs
- External provider adapters
- Ticket creation
- Transcript generation
- Role hierarchy and bot-position scenarios

### Regression Tests

Every production bug becomes a regression test before the fix is considered complete.

## 43. Implementation Phases

Features are implemented in phases rather than all at once.

### Phase 1: Foundation

- `zenkai/core/` (discord, database, permissions, config, scheduler, cache, logging) plus the `zenkai` entrypoint
- Slash command registry with one end-to-end canary command, button/select/modal plumbing
- Docker compose (bot + postgres + redis), `.env.example`, lint/test harness
- Database migrations and repositories; safe defaults seeded on guild join
- Event bus + scheduler with idempotent job support and recovery
- Audit log writer, error handling, health/status endpoint

### Phase 2: Community

- Welcome and roles
- XP, profiles, statistics (event-driven with anti-abuse guards and streak resets)
- Server stats collection and leaderboards

### Phase 3: Moderation and Support

- Moderation actions, logs, raid protection, user history
- Tickets with categories, claim/close/reopen, transcripts, deterministic inactivity auto-close
- Suggestions and bug lifecycles with AI formatting and staff transitions
- Backups and restore safeguards

### Phase 4: AI

- AI tools: `/ask`, `/anime`, `/manga`, `/explain`, `/character`, `/summarize`, `/suggest`, `/bug`, `/pollai`, `/modai`
- Controlled mention-based chat within AI-enabled channels
- Provider router with fallback ordering; provider-agnostic interfaces

### Phase 5: Anime

- Anime search, recommendations, characters, random
- Manga and manhwa
- Anime news polling with duplicate suppression
- Weekly/monthly awards

### Phase 6: Entertainment

- Games engine: trivia, guess the character, Akinator-style, random
- Polls with `/pollai` generation
- Giveaways with deterministic winner/reroll logic
- Events and watch parties with RSVP, reminders, attendance

### Phase 7: Automation

- Notifications for updates, reminders, status, tickets, giveaways, watch parties
- Status monitoring with retry and confirmation logic before alerting
- Ticket auto-management, news automation, scheduled events, automated backups

### Phase 8: Dashboard and Ops

- Complete admin dashboard sections and API hardening, per-server rate limits
- Tests per feature (unit, integration, regression)
- Documentation pass: every config field documented alongside implementation

### Milestones

- M1: canary slash command, config, scheduler, audit log end-to-end
- M2: welcome, roles, XP usable in one test server
- M3: AI tools with router and safety controls
- M4: anime, manga, games, polls, giveaways, events, watch parties
- M5: tickets, moderation, notifications, status, backups
- M6: dashboard complete, documentation, deployment, observability

## 44. Installation and Operations

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis (cache and scheduler state)
- Node 20+ (optional dashboard)
- A Discord application with `bot` and `applications.commands` scopes
- Intents approved and enabled in the Developer Portal to match the code: `Guilds`, `Members` (privileged), `Message Content` (privileged), `Reactions`, and `Voice` only when the matching feature is enabled

### Environment

```bash
cp .env.example .env
# DISCORD_TOKEN, DATABASE_URL, REDIS_URL
# AI_PROVIDER, AI_API_KEY, AI_MODEL            (per provider)
# DASHBOARD_CLIENT_ID, DASHBOARD_CLIENT_SECRET (only if the dashboard is enabled)
# STATUS_ENDPOINTS                              (optional external service health checks)
```

Provider keys and tokens are only loaded from environment or secret management. They are never written to logs, backups, database records, or custom command payloads.

### Quickstart

```bash
git clone <repo> && cd zenkai
cp .env.example .env
docker compose up -d db redis
pip install -r requirements.txt
alembic upgrade head
python -m zenkai            # Discord gateway + shared scheduler entrypoint
# optional dashboard
cd dashboard && npm i && npm run dev
```

Startup runs configuration validation, checks migrations, and verifies database, Redis, scheduler, and provider connectivity before enabling commands.

### Invite URL

```text
https://discord.com/oauth2/authorize?client_id=APP_ID&permissions=MINIMAL_PERMISSIONS&scope=bot+applications.commands
```

Use the smallest permission integer the enabled features require rather than the `Administrator` permission.

### Operational Requirements

Before production rollout, Zenkai must provide:

- Graceful startup and shutdown
- Database migration handling
- Bounded external request timeouts and retries
- Discord interaction response deadlines
- Scheduler recovery after restart
- Idempotency for critical jobs and callbacks
- Structured health reporting
- Secret-safe logging
- Backup and restoration safeguards
- Production-like interaction and integration tests
- Documented installation, configuration, troubleshooting, and recovery procedures

## 45. Troubleshooting

### General / Gateway

- Bot offline → verify `DISCORD_TOKEN`, intents configured in both the Developer Portal and code, privileged intents approved, and the process logs show no unexpected shutdown.
- Slash commands missing → check the `applications.commands` scope; wait for global sync or use guild sync in development.
- Health shows a failed dependency → confirm Docker services, provider keys, and required network endpoints.

### Feature Specific

- No XP → check `xp.enabled`, excluded channels/roles, cooldown, daily cap, Discord hierarchy for reward roles, and that `message.created` is wired to the bus.
- Roles not assigned → required `manage_roles`, bot role position above target roles, then the audit log entry.
- AI silent → `ai.enabled`, channel allowlist/denylist, enabled commands, provider key/quota, cooldown, and router fallback ordering.
- AI cannot answer anime facts → confirm the anime provider is healthy and the tool route is enabled; never let the model fabricate facts.
- Tickets stuck open → inactivity job running, grace-period reminder sent, scheduler health.
- Giveaway never ends → check UTC storage for `ends_at`, scheduler job running, job idempotency logs.
- News feed duplicate or down → check news sources, provider health, and the scheduled news job.
- Status alert never fires → confirm the status endpoint returns the expected contract and confirmation threshold.
- Backup failed → check writable volume, config validation, and the manual restore authorization guard.
- Rate limits tripping → raise per-user cooldown or cached provider usage before contacting the provider.

### Data / Deployment

- DB migration fails → `alembic history`, single head, per-feature migration order.
- Dashboard 403 → OAuth guild membership failing the `manage_guild` or section ACL.
- Scheduler missed a job → check restart recovery and job run metadata.

### General Guidance

Every unresolved incident becomes an issue; every production bug becomes a regression test before the fix ships.

## 46. MVP

The first production-ready Zenkai includes:

```text
Discord Core
├── Permissions
├── Configuration
├── Logging
└── Scheduler

Community
├── Welcome
├── Profiles
├── XP/Levels
└── Roles

Moderation
├── Basic moderation
├── Logs
├── Raid protection
└── Tickets

AI
├── /ask
├── /anime
├── /manga
├── /explain
├── /character
├── /summarize
├── /suggest
├── /bug
├── /pollai
└── /modai

Anime
├── Search
├── Recommendations
└── News

Entertainment
├── Trivia
├── Polls
├── Giveaways
└── Events
```

Everything else follows after the foundation proves stable.

## 47. Definition of Done

A feature is complete only when it has:

```text
Implementation
      ↓
Discord UX
      ↓
Permission checks
      ↓
Error handling
      ↓
Logging
      ↓
Database persistence where required
      ↓
Scheduler integration where required
      ↓
Tests
      ↓
Production verification
```

## 48. Design Rules

1. **Discord first:** Use Discord's native capabilities whenever possible.
2. **Modular:** Keep features independently understandable and testable.
3. **Minimal dependencies:** Add infrastructure only when it solves a demonstrated need.
4. **No unnecessary abstraction:** Avoid generic frameworks that only make the architecture appear complex.
5. **AI assists, humans control:** Especially for moderation and administration.
6. **Deterministic automation:** Time-based operations use the scheduler rather than AI decisions.
7. **Server-specific configuration:** Each Discord server can enable and configure features independently.
8. **Fail gracefully:** One external dependency failure should not take down Zenkai.
9. **Observable operations:** Logs and health information make production issues diagnosable.
10. **Regression protection:** Every production bug becomes a regression test.

## 49. Final Feature Map

```text
                         ZENKAI
                            │
 ┌──────────────────────────┼──────────────────────────┐
 │                          │                          │
 ▼                          ▼                          ▼
AI                       ANIME                   COMMUNITY
│                          │                          │
├ /ask                     ├ Anime Info               ├ Profiles
├ /anime                   ├ Recommendations          ├ XP
├ /manga                   ├ Characters               ├ Levels
├ /explain                 ├ Manga/Manhwa             ├ Badges
├ /suggest                 ├ Anime News               ├ Achievements
├ /bug                     └ Anime Awards             ├ Streaks
├ /summarize                                          └ Roles
├ /modai
├ /character
└ /pollai

 ┌──────────────────────────┼──────────────────────────┐
 │                          │                          │
 ▼                          ▼                          ▼
MODERATION             ENTERTAINMENT               SUPPORT
│                          │                          │
├ Moderation               ├ Trivia                   ├ Private Tickets
├ Raid Protection          ├ Guess Character          ├ Categories
├ Logs                     ├ Akinator                 ├ Claim
├ Suggestions              ├ Polls                    ├ Staff
├ Bug Reports              ├ Giveaways                ├ Transcripts
└ Backups                  ├ Events                   └ Auto-close
                           └ Watch Parties

 ┌──────────────────────────┼──────────────────────────┐
 │                          │                          │
 ▼                          ▼                          ▼
AUTOMATION               ANALYTICS                   ADMIN
│                          │                          │
├ Notifications            ├ Server Stats             ├ Dashboard
├ News Feed                ├ Member Growth            ├ Configuration
├ Status Monitor           ├ Activity                 ├ Custom Commands
├ Reminders                ├ Leaderboards             ├ AI Settings
└ Scheduled Jobs           └ Game/Event Stats         └ Permissions
```

## 50. Final Architecture Philosophy

Zenkai is one coherent Discord community assistant rather than a collection of unrelated bots.

The internal architecture is:

```text
Small Core
    +
Independent Features
    +
Shared Infrastructure
    +
Clear Interfaces
    +
Strong Permissions
    +
Deterministic Automation
    +
AI Assistance
```

The goal is not to build the largest possible bot. The goal is a deeply integrated anime-community bot whose features are useful, discoverable, reliable, and maintainable.