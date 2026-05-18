"""Development smoke helper for Unity-bound LiveKit RPC.

This stays outside the app runtime on purpose. It joins the configured LiveKit
room as a throwaway participant and performs one RPC call to the Unity client,
printing both transport errors and the raw Unity response.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

from livekit import rtc  # noqa: E402
from livekit.api import AccessToken, VideoGrants  # noqa: E402


UNITY_PROBE_IDENTITY_MARKERS = ("photo-node-probe",)


def _load_env_file(path: str) -> None:
    if not path:
        return
    env_path = Path(path)
    if not env_path.is_absolute():
        env_path = ROOT / env_path
    if not env_path.exists():
        return

    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _make_token(identity: str, room_name: str, api_key: str, api_secret: str) -> str:
    return (
        AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=False,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .with_ttl(timedelta(minutes=10))
        .to_jwt()
    )


def _is_probe(identity: str) -> bool:
    lowered = identity.lower()
    return any(marker in lowered for marker in UNITY_PROBE_IDENTITY_MARKERS)


def _iter_remote_identities(room: rtc.Room) -> list[str]:
    return [
        str(getattr(participant, "identity", "") or "")
        for participant in room.remote_participants.values()
        if str(getattr(participant, "identity", "") or "")
    ]


def _pick_target(room: rtc.Room, explicit: str) -> str:
    if explicit:
        return explicit

    first_unity = ""
    for identity in _iter_remote_identities(room):
        if not identity.lower().startswith("unity"):
            continue
        if not first_unity:
            first_unity = identity
        if not _is_probe(identity):
            return identity
    return first_unity


async def _wait_for_target(room: rtc.Room, explicit: str, timeout_s: float) -> str:
    deadline = asyncio.get_running_loop().time() + max(0.0, timeout_s)
    while asyncio.get_running_loop().time() < deadline:
        target = _pick_target(room, explicit)
        if target:
            return target
        await asyncio.sleep(0.25)
    return _pick_target(room, explicit)


def _parse_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.payload:
        parsed = json.loads(args.payload)
        if not isinstance(parsed, dict):
            raise ValueError("--payload must be a JSON object")
        return parsed

    if args.method == "animate":
        payload: dict[str, Any] = {"animation": args.animation}
        if args.strict_capability:
            payload["strict_capability"] = True
        return payload

    if args.method == "flyTo":
        raise ValueError("flyTo needs an explicit --payload JSON object to avoid accidental movement")

    return {
        "source": "tools/rpc_call_unity.py",
        "sent_at": time.time(),
    }


def _summarize_response(response: str) -> str:
    try:
        data = json.loads(response or "{}")
    except json.JSONDecodeError:
        return "non_json_response"
    if not isinstance(data, dict):
        return f"json_{type(data).__name__}"
    status = str(data.get("status", "") or "")
    reason = str(data.get("reason", "") or "")
    detail = str(data.get("detail") or data.get("message") or "")
    command_id = str(data.get("command_id", "") or "")
    return f"status={status or '<missing>'} reason={reason or '-'} detail={detail or '-'} command_id={command_id or '-'}"


async def _amain(args: argparse.Namespace) -> int:
    _load_env_file(args.env_file)
    livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    livekit_api_secret = os.getenv(
        "LIVEKIT_API_SECRET",
        "parrot_carriers_local_dev_livekit_secret_key_v1",
    )
    room_name = args.room or os.getenv("LIVEKIT_ROOM", "parrot-main")
    identity = args.identity
    token = _make_token(identity, room_name, livekit_api_key, livekit_api_secret)
    room = rtc.Room()

    print(f"[rpc_call_unity] connect url={livekit_url} room={room_name} identity={identity}")
    await room.connect(livekit_url, token)
    try:
        target = await _wait_for_target(room, args.target, args.wait_seconds)
        remotes = _iter_remote_identities(room)
        print(f"[rpc_call_unity] remotes={remotes}")
        if args.list_only:
            return 0
        if not target:
            print("[rpc_call_unity] ERROR no Unity participant found")
            return 2

        payload = _parse_payload(args)
        payload_json = json.dumps(payload, ensure_ascii=False)
        print(f"[rpc_call_unity] -> {target}.{args.method} payload={payload_json}")
        try:
            response = await room.local_participant.perform_rpc(
                destination_identity=target,
                method=args.method,
                payload=payload_json,
                response_timeout=args.response_timeout,
            )
        except Exception as exc:
            print(f"[rpc_call_unity] TRANSPORT_ERROR {type(exc).__name__}: {exc}")
            return 3

        print(f"[rpc_call_unity] RAW_RESPONSE {response}")
        print(f"[rpc_call_unity] SUMMARY {_summarize_response(response)}")
        return 0
    finally:
        await room.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-call a Unity LiveKit RPC method.")
    parser.add_argument("--identity", default="rpc-smoke-client")
    parser.add_argument(
        "--env-file",
        default="infra/laptop.env.local",
        help="Env file to seed LIVEKIT_* values when shell env is unset. Empty string disables it.",
    )
    parser.add_argument("--room", default="", help="LiveKit room override; defaults to LIVEKIT_ROOM.")
    parser.add_argument("--target", default="", help="Unity participant identity override.")
    parser.add_argument("--method", default="unitySmokeProbeEcho")
    parser.add_argument("--payload", default="", help="Raw JSON object payload.")
    parser.add_argument("--animation", default="idle", help="Default payload animation for --method animate.")
    parser.add_argument("--strict-capability", action="store_true")
    parser.add_argument("--wait-seconds", type=float, default=8.0)
    parser.add_argument("--response-timeout", type=float, default=5.0)
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args()

    try:
        return asyncio.run(_amain(args))
    except Exception as exc:
        print(f"[rpc_call_unity] ERROR {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
