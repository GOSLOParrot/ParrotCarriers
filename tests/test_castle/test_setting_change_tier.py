"""Phase 4.1+4.2 — setting_change_tier registry + RoomSettingService wire."""

from __future__ import annotations

import pytest

from parrot.brain import setting_change_tier as sct


def test_registry_loads() -> None:
    sct.reset_cache()
    registry = sct.load_tier_registry()
    assert registry["schema_version"] == 1
    assert "tiers" in registry
    assert "settings" in registry


def test_known_tier_lookups() -> None:
    sct.reset_cache()
    assert sct.tier_for("behavior_mode") == 0
    assert sct.tier_for("line_id") == 1
    assert sct.tier_for("GOOGLE_API_KEY") == 2
    assert sct.tier_for("livekit_yaml") == 3


def test_unknown_falls_back_to_safe_default() -> None:
    sct.reset_cache()
    assert sct.tier_for("totally_unknown_setting") == 2


def test_line_switch_tier_collapses_when_lines_match() -> None:
    sct.reset_cache()
    assert sct.line_switch_tier_for_profile("line_a", "line_a") == 0
    assert sct.line_switch_tier_for_profile("line_b", "line_a") == 1


def test_tier_label_and_summary_present() -> None:
    sct.reset_cache()
    assert sct.tier_label(0) == "BB-write"
    assert sct.tier_label(1) == "LiveKit reconnect"
    assert "instantly" in sct.tier_summary(0)
    assert "重启" in sct.tier_summary(2, lang="zh")


def test_room_setting_compatibility_carries_tier() -> None:
    """RoomSettingService.compatibility() must include ``tier`` on the report."""
    sct.reset_cache()
    from parrot.brain.preset_loader import RoomProfile, get_preset_loader
    from parrot.brain.room_setting import RoomSettingService

    loader = get_preset_loader()
    profile = next(iter(loader.list_room_profiles()), None)
    assert profile is not None, "fixture: at least one RoomProfile must exist"

    report = RoomSettingService().compatibility(profile)
    payload = report.as_json()
    assert "tier" in payload
    assert payload["tier"] in {0, 1, 2}
    assert "tier_label" in payload
    assert "tier_summary" in payload
    assert "tier_ui_action" in payload


def test_line_selector_carries_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each line selector emits its own tier so UI can render per-row dialogs."""
    sct.reset_cache()
    from parrot.brain.app_first_version import AppFirstVersionFacade

    monkeypatch.setenv("PARROT_LLM_PIPELINE", "line_a")
    snapshot = AppFirstVersionFacade().room_setting_snapshot(None).as_json()
    selectors = snapshot.get("selectors", {})
    lines = selectors.get("lines", []) or []
    assert lines, "selectors must list at least line_a + line_b"
    for line in lines:
        policy = line.get("selection_policy") or {}
        assert "tier" in policy
        assert "tier_summary" in policy
        if line.get("line_id") == "line_a":
            assert policy["tier"] == 0
        if line.get("line_id") == "line_b":
            assert policy["tier"] == 1
