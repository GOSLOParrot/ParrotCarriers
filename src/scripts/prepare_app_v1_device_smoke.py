"""Prepare App V1 real-device smoke-test connection values.

This helper does not mint tokens or write Unity secrets. It only gathers the
LAN-facing URLs a phone build needs so the human smoke test can avoid
localhost mistakes.
"""

from __future__ import annotations

import argparse
import json
import socket
import time
from pathlib import Path
from typing import Any


def discover_lan_host() -> str:
    """Best-effort LAN IP discovery without sending payload data."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        host = sock.getsockname()[0]
    except OSError:
        host = socket.gethostbyname(socket.gethostname())
    finally:
        sock.close()
    return host


def build_smoke_config(
    *,
    lan_host: str,
    room_id: str,
    identity: str,
    livekit_port: int,
    token_mint_port: int,
    photo_upload_port: int,
    monitor_port: int,
) -> dict[str, Any]:
    """Return the phone-facing smoke config and checklist."""
    return {
        "schema_version": 1,
        "generated_at_unix": int(time.time()),
        "lan_host": lan_host,
        "unity_runtime": {
            "room_id": room_id,
            "unity_identity": identity,
            "livekit_url": f"ws://{lan_host}:{livekit_port}",
            "token_mint_endpoint": f"http://{lan_host}:{token_mint_port}/mint",
            "photo_upload_host": lan_host,
            "photo_upload_port": photo_upload_port,
            "web_console_url": f"http://{lan_host}:{monitor_port}/",
        },
        "phone_preflight": [
            "Phone and workstation are on the same LAN or VPN.",
            "LiveKit server is reachable from phone on the listed ws:// URL.",
            "Token mint endpoint returns a short-lived token for the room.",
            "Brain monitor/Web console opens from the phone browser.",
            "Photo upload endpoint accepts POST /upload/photo/{photo_id}.",
            "Unity build has camera, microphone, and network permissions.",
            "ARCore/ARKit tracking starts before testing tools.",
            "GOSLO is not allowed to greet until onGosloPlaced is sent.",
        ],
        "tool_smoke_order": [
            "Start AR",
            "SceneReady",
            "GOSLO Placed",
            "Camera preview",
            "Camera capture",
            "Magnifier focus",
            "BoundaryBox place/resize/remove",
            "Nanobot paper note",
            "Paper note select/drag/scale",
            "Paper note drag to trash and workdesk targets",
            "Workdesk accept/dismiss/archive",
            "Parrot joystick walk and return-to-desk",
            "XRHand debug branch or real index-middle perch",
            "Silent/Voice/Full AR mode switch",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lan-host", default="", help="Override detected LAN IP/host.")
    parser.add_argument("--room-id", default="parrot-main")
    parser.add_argument("--identity", default="unity-device-smoke")
    parser.add_argument("--livekit-port", type=int, default=7880)
    parser.add_argument("--token-mint-port", type=int, default=7888)
    parser.add_argument("--photo-upload-port", type=int, default=7889)
    parser.add_argument("--monitor-port", type=int, default=7892)
    parser.add_argument("--write", type=Path, default=None, help="Optional JSON output path.")
    parser.add_argument("--print", action="store_true", help="Print JSON to stdout.")
    args = parser.parse_args()

    lan_host = args.lan_host.strip() or discover_lan_host()
    config = build_smoke_config(
        lan_host=lan_host,
        room_id=args.room_id,
        identity=args.identity,
        livekit_port=args.livekit_port,
        token_mint_port=args.token_mint_port,
        photo_upload_port=args.photo_upload_port,
        monitor_port=args.monitor_port,
    )
    payload = json.dumps(config, ensure_ascii=False, indent=2)

    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(payload + "\n", encoding="utf-8")
    if args.print or args.write is None:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
