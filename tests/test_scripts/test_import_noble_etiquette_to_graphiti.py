from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_module():
    script_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "scripts"
        / "import_noble_etiquette_to_graphiti.py"
    )
    spec = importlib.util.spec_from_file_location("import_noble_etiquette_to_graphiti", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sample_text() -> str:
    return """INTRODUCTION.

Introductory etiquette notes.

CONTENTS.

CHAPTER I.

  CONVERSATION                                                11

CHAPTER II.

  DRESS                                                       21

LADIES' BOOK OF ETIQUETTE.

CHAPTER I.

CONVERSATION.

Conversation body paragraph.

CHAPTER II.

DRESS.

Dress body paragraph.
"""


def test_build_episodes_skips_contents_and_keeps_chapter_one(tmp_path: Path) -> None:
    module = _load_module()
    text_path = tmp_path / "pg35123.txt"
    text_path.write_text(_sample_text(), encoding="utf-8")

    episodes = module.build_episodes(text_path, max_chars=2000)

    chapter_ids = [item.chapter_id for item in episodes]
    assert chapter_ids == ["intro", "chapter_01", "chapter_02"]
    assert episodes[0].name.startswith("noble_etiquette_pg35123_v2_intro_")
    assert "CONTENTS." not in episodes[0].episode_body
    assert episodes[1].chapter_title == "Conversation."
    assert "Conversation body paragraph." in episodes[1].episode_body


def test_build_episodes_uses_repo_relative_source_file_ref(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _load_module()
    repo = tmp_path / "repo"
    source_dir = repo / "Noble Etiquette"
    source_dir.mkdir(parents=True)
    text_path = source_dir / "pg35123.txt"
    text_path.write_text(_sample_text(), encoding="utf-8")
    monkeypatch.setattr(module, "REPO_ROOT", repo)

    episodes = module.build_episodes(text_path, max_chars=2000)

    assert "source_file: Noble Etiquette/pg35123.txt" in episodes[0].episode_body
    assert str(tmp_path) not in episodes[0].episode_body


def test_main_returns_failure_when_graphiti_api_reports_failure(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    module = _load_module()
    text_path = tmp_path / "pg35123.txt"
    text_path.write_text(_sample_text(), encoding="utf-8")

    def fake_post_episode(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"success": False, "message": "provider failed"}

    monkeypatch.setattr(module, "_post_episode", fake_post_episode)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "import_noble_etiquette_to_graphiti.py",
            "--apply",
            "--text",
            str(text_path),
            "--limit",
            "1",
            "--no-skip-existing",
        ],
    )

    assert module.main() == 1
    output = capsys.readouterr().out
    assert '"success": false' in output
    assert '"error_count": 1' in output
