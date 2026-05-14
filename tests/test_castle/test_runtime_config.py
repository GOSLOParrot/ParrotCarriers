"""Phase 1 ECS Orchestrator — runtime_config layering tests.

Plan reference: ``.cursor/memory/architecture/Interface/app_v1_brain_cold_start_line_lifecycle_audit_20260511.md``
Phase 1 §T1.2 / T1.3 / T1.5.

Covers:

* Resolution order: file > BB > env > default for line_id /
  line_profile_id / room_profile_id.
* ``source`` map reports the layer that won, per field.
* ``write_runtime_config`` is partial (preserves untouched keys) and
  validates ``line_id``.
* ``write_brain_runtime_snapshot`` puts a snapshot on BB and
  ``clear_brain_runtime_snapshot`` removes it.
* Brain ``_resolve_pipeline()`` honours the new layering (file beats
  env), and the default is preserved when both are absent.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture()
def tmp_runtime_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Point runtime_config at an isolated temp file.

    Also stubs ``_bb_get`` to return ``None`` by default so a dev
    machine with a populated Redis cannot leak BB values into the
    test. Individual tests that need a non-None BB value re-patch
    ``_bb_get`` themselves.
    """
    target = tmp_path / "runtime_config.json"
    monkeypatch.setenv("PARROT_RUNTIME_CONFIG_PATH", str(target))
    monkeypatch.delenv("PARROT_LLM_PIPELINE", raising=False)
    monkeypatch.delenv("PARROT_ACTIVE_LINE_PROFILE_ID", raising=False)
    monkeypatch.delenv("PARROT_ACTIVE_ROOM_PROFILE_ID", raising=False)
    monkeypatch.delenv("PARROT_LINE_PROFILE", raising=False)
    import parrot.castle.runtime_config as rc

    monkeypatch.setattr(rc, "_bb_get", lambda key: None)
    return target


def test_default_when_nothing_set(tmp_runtime_config: Path) -> None:
    from parrot.castle.runtime_config import resolve_runtime_config

    resolved = resolve_runtime_config()
    assert resolved.line_id == "line_a"
    assert resolved.line_profile_id == ""
    assert resolved.room_profile_id == ""
    assert resolved.source == {
        "line_id": "default",
        "line_profile_id": "default",
        "room_profile_id": "default",
    }
    assert resolved.file_present is False


def test_env_only(monkeypatch: pytest.MonkeyPatch, tmp_runtime_config: Path) -> None:
    from parrot.castle.runtime_config import resolve_runtime_config

    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_b")
    monkeypatch.setenv("PARROT_ACTIVE_LINE_PROFILE_ID", "lineb_google_default")

    resolved = resolve_runtime_config()
    assert resolved.line_id == "line_b"
    assert resolved.line_profile_id == "lineb_google_default"
    assert resolved.source["line_id"] == "env"
    assert resolved.source["line_profile_id"] == "env"


def test_file_beats_env(monkeypatch: pytest.MonkeyPatch, tmp_runtime_config: Path) -> None:
    from parrot.castle.runtime_config import resolve_runtime_config

    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_a")
    tmp_runtime_config.write_text(
        json.dumps({"line_id": "line_b"}), encoding="utf-8"
    )
    resolved = resolve_runtime_config()
    assert resolved.line_id == "line_b"
    assert resolved.source["line_id"] == "file"


def test_unknown_line_in_file_falls_through(
    monkeypatch: pytest.MonkeyPatch, tmp_runtime_config: Path
) -> None:
    """An unrecognised file value must be ignored, not propagated."""
    from parrot.castle.runtime_config import resolve_runtime_config

    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_b")
    tmp_runtime_config.write_text(
        json.dumps({"line_id": "line_z_typo"}), encoding="utf-8"
    )
    resolved = resolve_runtime_config()
    assert resolved.line_id == "line_b"
    assert resolved.source["line_id"] == "env"


def test_write_partial_preserves_other_keys(tmp_runtime_config: Path) -> None:
    from parrot.castle.runtime_config import (
        resolve_runtime_config,
        write_runtime_config,
    )

    write_runtime_config(
        line_id="line_b",
        line_profile_id="lineb_ner_ja_test",
        room_profile_id="ner_lineb_room",
        updated_by="test_setup",
    )
    write_runtime_config(line_id="line_a", updated_by="test_partial")

    resolved = resolve_runtime_config()
    assert resolved.line_id == "line_a"
    assert resolved.line_profile_id == "lineb_ner_ja_test"
    assert resolved.room_profile_id == "ner_lineb_room"


def test_write_rejects_bad_line_id(tmp_runtime_config: Path) -> None:
    from parrot.castle.runtime_config import write_runtime_config

    with pytest.raises(ValueError):
        write_runtime_config(line_id="line_z_invalid")


def test_write_rejects_empty_string_ids(tmp_runtime_config: Path) -> None:
    from parrot.castle.runtime_config import write_runtime_config

    with pytest.raises(ValueError):
        write_runtime_config(line_profile_id="")
    with pytest.raises(ValueError):
        write_runtime_config(room_profile_id="   ")


def test_clear_runtime_config_idempotent(tmp_runtime_config: Path) -> None:
    from parrot.castle.runtime_config import (
        clear_runtime_config,
        resolve_runtime_config,
        write_runtime_config,
    )

    write_runtime_config(line_id="line_b", updated_by="test")
    assert clear_runtime_config() is True
    assert clear_runtime_config() is False  # already gone, missing_ok
    assert resolve_runtime_config().line_id == "line_a"


def test_brain_resolve_pipeline_honours_runtime_file(
    monkeypatch: pytest.MonkeyPatch, tmp_runtime_config: Path
) -> None:
    """Brain agent must use file > env when picking the pipeline.

    This is the core Phase 1 promise: the orchestrator can flip Line
    by writing a file, without touching the running Brain process's
    env. Then the next ``brain_entrypoint`` reads the new value.
    """
    from parrot.castle.runtime_config import write_runtime_config

    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_a")

    # Re-import agent module to pick up the fresh env.
    import parrot.brain.agent as agent_mod

    importlib.reload(agent_mod)

    assert agent_mod._resolve_pipeline() == "line_a"

    write_runtime_config(line_id="line_b", updated_by="test_resolve")
    assert agent_mod._resolve_pipeline() == "line_b"


def test_running_line_id_ignores_bb_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_runtime_config: Path
) -> None:
    """Bug O regression: BB-only writes must not flip running_line_id.

    The runtime_config layering reserves "running" for file/env/default.
    A BB write to ``global/active_line_id`` represents the *selected*
    intent, not what the live Brain process is serving — surfacing it
    as "running" was the original Round 5 Bug O.
    """
    from parrot.brain.line_status import running_line_id

    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_a")

    # Patch the BB read inside runtime_config to return a drifted
    # value, simulating a partial supervisor restart that wrote BB
    # without updating env.
    import parrot.castle.runtime_config as rc

    monkeypatch.setattr(rc, "_bb_get", lambda key: "line_b")

    assert running_line_id() == "line_a"


def test_brain_runtime_snapshot_round_trip(
    monkeypatch: pytest.MonkeyPatch, tmp_runtime_config: Path
) -> None:
    """write_brain_runtime_snapshot persists what next session will see."""
    from parrot.castle.runtime_config import (
        clear_brain_runtime_snapshot,
        write_brain_runtime_snapshot,
        write_runtime_config,
    )

    captured: dict[str, Any] = {}

    class _FakeBB:
        def set(self, key: str, value: Any) -> None:
            captured[key] = value

    monkeypatch.setattr(
        "parrot.scheduler.blackboard.open_bb_client",
        lambda **kw: _FakeBB(),
    )

    write_runtime_config(line_id="line_b", updated_by="test_snapshot")
    snap = write_brain_runtime_snapshot(
        pid=4242,
        room_name="parrot-test",
        started_at=1234567890.0,
        extra={"resolved_pipeline": "line_b"},
    )
    assert captured["global/brain_runtime_snapshot"]["line_id"] == "line_b"
    assert captured["global/brain_runtime_snapshot"]["pid"] == 4242
    assert captured["global/brain_runtime_snapshot"]["room_name"] == "parrot-test"
    assert captured["global/brain_runtime_snapshot"]["resolved_pipeline"] == "line_b"
    assert snap["source"]["line_id"] == "file"

    clear_brain_runtime_snapshot()
    assert captured["global/brain_runtime_snapshot"] is None


def test_force_unity_reconnect_rpc_registered() -> None:
    """Static check: forceUnityReconnect stays on the real-time RPC surface.

    Until livekit-agents grows a real test harness, this is the
    cheapest guard against a future refactor accidentally dropping
    the handler.
    """
    from pathlib import Path

    text = Path("src/parrot/brain/agent.py").read_text(encoding="utf-8")
    assert 'register_rpc_method("forceUnityReconnect")' in text
    assert "await room.disconnect()" in text
    # Logger registration line must mention it so an operator can
    # grep ECS logs for "forceUnityReconnect" and find both sides.
    assert "forceUnityReconnect" in text
