from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT = ROOT / "src" / "parrot" / "brain" / "agent.py"
APP_MONITOR = ROOT / "src" / "parrot" / "brain" / "app_monitor_server.py"


def test_legacy_menu_persistence_rpcs_are_not_registered() -> None:
    text = AGENT.read_text(encoding="utf-8")

    for method in [
        "listMenuBlocks",
        "applyMenuSelection",
        "applyPreset",
        "saveAsPreset",
        "getRoomSettingSnapshot",
        "previewRoomProfile",
        "newRoomProfile",
        "saveRoomProfile",
    ]:
        assert f'register_rpc_method("{method}")' not in text


def test_realtime_app_rpc_surface_is_classified_and_compact() -> None:
    text = AGENT.read_text(encoding="utf-8")

    assert "def _attach_realtime_app_rpc" in text
    assert "Durable App surfaces are intentionally HTTP-owned" in text
    assert "Category A: START / session sync" in text
    assert "Category B: LineB / audio route diagnostics" in text
    assert "Category C: in-room workspace control" in text
    assert "Category D: compact media/module controls" in text
    assert "Category E: ops/governance signal" in text
    assert "Realtime App RPC handlers registered" in text
    assert "ctx.room.disconnect()" not in text
    assert "await room.disconnect()" in text
    assert "not RoomSetting's skin/theme" in text

    for method in [
        "applyRoomProfile",
        "setAppCapabilityMode",
        "setLineBAudioRoutePolicy",
        "registerLineBTtsSegment",
        "classifyLineBMicInput",
        "verifyLineBVoiceprintEmbedding",
        "applyWorkspace",
        "setPhotoAwareness",
        "setCameraMode",
        "setXrHandMode",
        "forceUnityReconnect",
    ]:
        assert f'register_rpc_method("{method}")' in text


def test_full_app_menu_and_roomsetting_surfaces_stay_http_owned() -> None:
    text = APP_MONITOR.read_text(encoding="utf-8")

    for route in [
        '"/api/app/canvas"',
        '"/api/app/modules"',
        '"/api/app/tool-cabinet"',
        '"/api/app/personas"',
        '"/api/app/line-profiles"',
        '"/api/app/room-setting"',
        '"/api/app/room-setting/new"',
        '"/api/app/room-setting/save"',
        '"/api/app/room-setting/apply"',
    ]:
        assert route in text
