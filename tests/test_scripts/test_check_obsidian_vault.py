from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    script_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "scripts"
        / "check_obsidian_vault.py"
    )
    spec = importlib.util.spec_from_file_location("check_obsidian_vault", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Dataclasses resolve postponed annotations through sys.modules during
    # dynamic imports, so the test mirrors normal import registration.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_check_vault_reports_ingest_ready_note(tmp_path: Path) -> None:
    module = _load_module()
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "mug.md").write_text(
        """---
profile: "daily"
kind: "object"
title: "Blue mug"
---

Used for coffee.
""",
        encoding="utf-8",
    )

    result = module.check_vault(vault)

    assert result.status == "ingest_ready"
    assert result.markdown_count == 1
    assert result.ingest_ready_count == 1
    assert result.profile_counts == {"daily": 1}
    assert result.sample_ready_notes[0]["path"] == "mug.md"
    assert result.sample_ready_notes[0]["obsidian_uuid"] == ""


def test_check_vault_requires_uuid_only_for_ref_notes(tmp_path: Path) -> None:
    module = _load_module()
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "ref_without_uuid.md").write_text(
        """---
profile: "ref"
title: "Blue mug ref"
---

This ref note cannot bind without a UUID.
""",
        encoding="utf-8",
    )

    result = module.check_vault(vault)

    assert result.status == "reachable_not_ingest_ready"
    assert result.markdown_count == 1
    assert result.ingest_ready_count == 0


def test_check_vault_reports_reachable_but_not_ingest_ready(tmp_path: Path) -> None:
    module = _load_module()
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "welcome.md").write_text("Hello GOSLO", encoding="utf-8")
    (vault / ".obsidian").mkdir()
    (vault / ".obsidian" / "ignored.md").write_text("Not a memory note", encoding="utf-8")

    result = module.check_vault(vault)

    assert result.status == "reachable_not_ingest_ready"
    assert result.markdown_count == 1
    assert result.ingest_ready_count == 0
    assert result.invalid_count == 1
    assert result.sample_invalid_notes == ["welcome.md"]
