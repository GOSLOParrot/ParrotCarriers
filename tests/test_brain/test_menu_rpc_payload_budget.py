import json
from dataclasses import asdict, is_dataclass

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


def test_menu_blocks_rpc_snapshot_stays_below_control_payload_budget() -> None:
    menu = MenuRegistry().list_blocks()
    payload = json.dumps(
        {"status": "ok", "snapshot": _to_rpc_wire(menu)},
        ensure_ascii=False,
    )

    assert len(payload.encode("utf-8")) < 15_000
