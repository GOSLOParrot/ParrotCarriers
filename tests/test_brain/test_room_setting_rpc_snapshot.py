import json
from dataclasses import asdict, is_dataclass

from parrot.brain.agent import _compact_room_setting_snapshot_for_rpc
from parrot.brain.app_first_version import AppFirstVersionFacade
from parrot.brain.menu_registry import MenuRegistry


def _to_rpc_wire(obj):
    if is_dataclass(obj):
        return _to_rpc_wire(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): _to_rpc_wire(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_rpc_wire(v) for v in obj]
    if hasattr(obj, "name") and hasattr(obj, "value"):
        return getattr(obj, "name")
    return obj


def test_room_setting_rpc_snapshot_compacts_below_livekit_rpc_limit() -> None:
    snapshot = AppFirstVersionFacade().room_setting_snapshot().as_json()

    compact = _compact_room_setting_snapshot_for_rpc(snapshot)
    payload = json.dumps({"status": "ok", "snapshot": compact, "compact": True}, ensure_ascii=False)

    assert len(payload.encode("utf-8")) < 15_000
    assert compact["active_room"]["room_profile_id"] == snapshot["active_room"]["room_profile_id"]
    assert compact["selectors"]["lines"]
    assert compact["selectors"]["experience_modes"]
    assert compact["selectors"]["skins"]


def test_menu_blocks_rpc_snapshot_stays_below_control_payload_budget() -> None:
    menu = MenuRegistry().list_blocks()
    payload = json.dumps(
        {"status": "ok", "snapshot": _to_rpc_wire(menu)},
        ensure_ascii=False,
    )

    assert len(payload.encode("utf-8")) < 15_000
