import json

from parrot.brain.agent import _compact_room_setting_snapshot_for_rpc
from parrot.brain.app_first_version import AppFirstVersionFacade


def test_room_setting_rpc_snapshot_compacts_below_livekit_rpc_limit() -> None:
    snapshot = AppFirstVersionFacade().room_setting_snapshot().as_json()

    compact = _compact_room_setting_snapshot_for_rpc(snapshot)
    payload = json.dumps({"status": "ok", "snapshot": compact, "compact": True}, ensure_ascii=False)

    assert len(payload.encode("utf-8")) < 15_000
    assert compact["active_room"]["room_profile_id"] == snapshot["active_room"]["room_profile_id"]
    assert compact["selectors"]["lines"]
    assert compact["selectors"]["experience_modes"]
    assert compact["selectors"]["skins"]
