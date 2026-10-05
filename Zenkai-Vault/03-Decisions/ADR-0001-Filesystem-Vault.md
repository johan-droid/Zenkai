---
tags: [zenkai, adr, architecture]
status: accepted
created: 2026-09-24
---

# ADR-0001: Filesystem-Backed Obsidian Vault

## Status

Accepted

## Context

The project needs a durable memory and documentation workspace that is compatible with Obsidian, easy to inspect without a service, and usable by an MCP client without a database or network service.

## Decision

Use the repository folder `Zenkai-Vault/` as an Obsidian-compatible filesystem vault. Markdown files are the source of truth. A standalone Python MCP server in `Zenkai-MCP/` exposes safe note operations over stdio.

The MCP server:

- Resolves every path against the configured vault root
- Rejects path traversal and symlink escapes
- Restricts note operations to `.md` files
- Uses atomic writes
- Limits note size
- Provides explicit search, append, and project-memory tools
- Does not expose delete or arbitrary command execution

## Consequences

- Notes remain readable and portable without Obsidian or a running service.
- Changes can be made manually or through MCP.
- Search is local and simple; a larger vault may eventually need indexing.
- The vault must be reviewed for secrets before sharing or committing.
