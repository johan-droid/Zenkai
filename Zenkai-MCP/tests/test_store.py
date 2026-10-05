from pathlib import Path

import pytest

from zenkai_vault_mcp.server import VaultStore


def test_store_reads_and_writes_markdown(tmp_path: Path) -> None:
    store = VaultStore(tmp_path / "vault")

    path = store.write("01-Projects/Project.md", "# Project\n")
    assert path == "01-Projects/Project.md"
    assert store.read(path) == "# Project\n"

    with pytest.raises(ValueError, match="extension"):
        store.write("01-Projects/Project.txt", "not markdown")


def test_store_rejects_path_traversal(tmp_path: Path) -> None:
    store = VaultStore(tmp_path / "vault")

    with pytest.raises(ValueError, match="escapes"):
        store.write("../outside.md", "no")


def test_store_appends_and_searches(tmp_path: Path) -> None:
    store = VaultStore(tmp_path / "vault")
    store.write("01-Projects/Memory.md", "# Memory\n")

    store.append("01-Projects/Memory.md", "Decision recorded.")
    results = store.search("decision", limit=10)

    assert results[0]["path"] == "01-Projects/Memory.md"
    assert results[0]["line"] == 3


def test_store_creates_folders_and_info(tmp_path: Path) -> None:
    store = VaultStore(tmp_path / "vault")
    store.create_folder("07-Logs")
    store.write("07-Logs/Entry.md", "entry")

    info = store.info()

    assert info["note_count"] == 1
    assert "07-Logs" in info["path"] or info["folder_count"] >= 1
