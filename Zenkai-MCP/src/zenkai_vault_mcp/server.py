from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

MAX_NOTE_BYTES = 2_000_000
DEFAULT_VAULT_PATH = Path(__file__).resolve().parents[3] / "Zenkai-Vault"
PROJECT_MEMORY_NOTE = "01-Projects/Zenkai-Project-Memory.md"


class VaultStore:
    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str, *, markdown: bool = False) -> Path:
        if not relative_path.strip():
            raise ValueError("path cannot be empty")
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError("path escapes the configured vault")
        if markdown and candidate.suffix.lower() != ".md":
            raise ValueError("note paths must use the .md extension")
        return candidate

    def relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def note_paths(self) -> list[Path]:
        notes: list[Path] = []
        for candidate in self.root.rglob("*.md"):
            try:
                resolved = self.resolve(self.relative(candidate), markdown=True)
            except ValueError:
                continue
            if resolved.is_file():
                notes.append(resolved)
        return sorted(notes)

    def folder_paths(self) -> list[Path]:
        folders: list[Path] = []
        for candidate in self.root.rglob("*"):
            if not candidate.is_dir() or candidate.name.startswith("."):
                continue
            try:
                resolved = candidate.resolve()
                resolved.relative_to(self.root)
            except ValueError:
                continue
            folders.append(resolved)
        return sorted(folders)

    def read(self, relative_path: str) -> str:
        path = self.resolve(relative_path, markdown=True)
        if not path.is_file():
            raise FileNotFoundError(f"note does not exist: {relative_path}")
        return path.read_text(encoding="utf-8")

    def write(self, relative_path: str, content: str, *, overwrite: bool = True) -> str:
        if len(content.encode("utf-8")) > MAX_NOTE_BYTES:
            raise ValueError(f"note exceeds the {MAX_NOTE_BYTES}-byte limit")
        path = self.resolve(relative_path, markdown=True)
        if path.exists() and not overwrite:
            raise FileExistsError(f"note already exists: {relative_path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=".zenkai-note-",
            dir=path.parent,
        )
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as temporary_file:
                temporary_file.write(content)
            os.replace(temporary_name, path)
        finally:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()
        return self.relative(path)

    def append(self, relative_path: str, content: str) -> str:
        if not self.resolve(relative_path, markdown=True).exists():
            return self.write(relative_path, content)
        existing = self.read(relative_path)
        if not existing:
            separator = ""
        elif existing.endswith("\n\n"):
            separator = ""
        else:
            separator = "\n"
        return self.write(relative_path, f"{existing}{separator}{content}")

    def create_folder(self, relative_path: str) -> str:
        if not relative_path.strip():
            raise ValueError("folder path cannot be empty")
        path = self.resolve(relative_path)
        if path.suffix.lower() == ".md":
            raise ValueError("folder path must not use the .md extension")
        path.mkdir(parents=True, exist_ok=True)
        return self.relative(path)

    def search(self, query: str, limit: int) -> list[dict[str, Any]]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            raise ValueError("query cannot be empty")
        bounded_limit = min(max(limit, 1), 100)
        results: list[dict[str, Any]] = []
        for path in self.note_paths():
            content = path.read_text(encoding="utf-8")
            for line_number, line in enumerate(content.splitlines(), start=1):
                if normalized_query not in line.lower():
                    continue
                results.append(
                    {
                        "path": self.relative(path),
                        "line": line_number,
                        "excerpt": line.strip()[:300],
                    }
                )
                if len(results) >= bounded_limit:
                    return results
        return results

    def info(self) -> dict[str, Any]:
        return {
            "path": str(self.root),
            "note_count": len(self.note_paths()),
            "folder_count": len(self.folder_paths()),
            "project_memory_note": PROJECT_MEMORY_NOTE,
            "project_memory_exists": self.resolve(PROJECT_MEMORY_NOTE).is_file(),
        }


def configured_store() -> VaultStore:
    configured_path = Path(os.getenv("ZENKAI_VAULT_PATH", str(DEFAULT_VAULT_PATH)))
    return VaultStore(configured_path)


store = configured_store()
mcp = FastMCP("zenkai-obsidian-vault")


@mcp.tool()
def vault_info() -> dict[str, Any]:
    """Return the vault location and current note/folder counts."""
    return store.info()


@mcp.tool()
def list_notes() -> list[dict[str, Any]]:
    """List all Markdown notes in the vault."""
    return [
        {
            "path": store.relative(path),
            "title": path.stem,
            "bytes": path.stat().st_size,
        }
        for path in store.note_paths()
    ]


@mcp.tool()
def read_note(path: str) -> str:
    """Read one Markdown note from the vault."""
    return store.read(path)


@mcp.tool()
def write_note(path: str, content: str, overwrite: bool = True) -> dict[str, str]:
    """Create or replace one Markdown note."""
    return {"path": store.write(path, content, overwrite=overwrite)}


@mcp.tool()
def append_note(path: str, content: str) -> dict[str, str]:
    """Append content to one Markdown note."""
    return {"path": store.append(path, content)}


@mcp.tool()
def search_notes(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Search Markdown note contents and return matching excerpts."""
    return store.search(query, limit)


@mcp.tool()
def list_folders() -> list[str]:
    """List folders in the vault."""
    return [store.relative(path) for path in store.folder_paths()]


@mcp.tool()
def create_folder(path: str) -> dict[str, str]:
    """Create a folder inside the vault."""
    return {"path": store.create_folder(path)}


@mcp.tool()
def append_project_memory(entry: str, path: str = PROJECT_MEMORY_NOTE) -> dict[str, str]:
    """Append a timestamped project-memory update to a Markdown note."""
    if not entry.strip():
        raise ValueError("memory entry cannot be empty")
    note_path = store.resolve(path, markdown=True)
    if not note_path.exists():
        store.write(path, "# Zenkai Project Memory\n\n## Memory Updates\n")
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    store.append(path, f"## {timestamp}\n\n{entry.strip()}\n")
    return {"path": store.relative(note_path)}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
