"""Development RPC smoke matrix for the laptop Castle room.

The script joins LiveKit as a throwaway participant and probes the safe RPC
surface without touching app runtime code.  It is intentionally conservative:
Unity-bound movement/perch/video-tier calls are opt-in because they can move
the visible model or alter media settings.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

from livekit import rtc  # noqa: E402
from livekit.api import AccessToken, VideoGrants  # noqa: E402


UNITY_PROBE_IDENTITY_MARKERS = ("photo-node-probe",)
DEFAULT_LOCAL_SECRET = "parrot_carriers_local_dev_livekit_secret_key_v1"


@dataclass(frozen=True)
class RpcCase:
    direction: str
    method: str
    payload: dict[str, Any]
    expected: str = "ok"


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


def _candidate_livekit_urls(raw_url: str, explicit: str) -> list[str]:
    if explicit:
        return [explicit]

    urls: list[str] = []
    for url in [raw_url or "ws://localhost:7880"]:
        if url and url not in urls:
            urls.append(url)

        parsed = urlparse(url)
        if parsed.scheme not in {"ws", "wss"}:
            continue
        host = (parsed.hostname or "").lower()
        port = parsed.port
        if not port or host in {"127.0.0.1", "localhost", "::1"}:
            continue
        local = f"{parsed.scheme}://127.0.0.1:{port}"
        if local not in urls:
            urls.append(local)
    return urls


async def _connect_room(
    *,
    urls: list[str],
    identity: str,
    room_name: str,
    api_key: str,
    api_secret: str,
) -> tuple[rtc.Room, str]:
    token = _make_token(identity, room_name, api_key, api_secret)
    last_error = ""
    for url in urls:
        room = rtc.Room()
        try:
            print(f"[rpc_smoke_matrix] connect url={url} room={room_name} identity={identity}")
            await room.connect(url, token)
            return room, url
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            print(f"[rpc_smoke_matrix] connect failed url={url} error={last_error}")
            try:
                await room.disconnect()
            except Exception:
                pass
    raise RuntimeError(f"could not connect to LiveKit ({last_error})")


def _remote_identities(room: rtc.Room) -> list[str]:
    return [
        str(getattr(participant, "identity", "") or "")
        for participant in room.remote_participants.values()
        if str(getattr(participant, "identity", "") or "")
    ]


def _is_probe(identity: str) -> bool:
    lowered = identity.lower()
    return any(marker in lowered for marker in UNITY_PROBE_IDENTITY_MARKERS)


def _pick_unity(room: rtc.Room, explicit: str) -> str:
    if explicit:
        return explicit
    first_unity = ""
    for identity in _remote_identities(room):
        if not identity.lower().startswith("unity"):
            continue
        if not first_unity:
            first_unity = identity
        if not _is_probe(identity):
            return identity
    return first_unity


def _pick_brain(room: rtc.Room, explicit: str) -> str:
    if explicit:
        return explicit
    for identity in _remote_identities(room):
        if identity.startswith("agent-") or identity == "brain":
            return identity
    return ""


async def _wait_for_targets(room: rtc.Room, args: argparse.Namespace) -> tuple[str, str]:
    deadline = asyncio.get_running_loop().time() + max(0.0, args.wait_seconds)
    brain = ""
    unity = ""
    while asyncio.get_running_loop().time() < deadline:
        brain = _pick_brain(room, args.brain_target)
        unity = _pick_unity(room, args.unity_target)
        if brain and (unity or args.brain_only):
            break
        if unity and (brain or args.unity_only):
            break
        await asyncio.sleep(0.25)
    return _pick_brain(room, args.brain_target), _pick_unity(room, args.unity_target)


def _safe_brain_cases() -> list[RpcCase]:
    return [
        RpcCase("brain", "setCameraMode", {"mode": "preview"}),
        RpcCase("brain", "setCameraMode", {"mode": "off"}),
        RpcCase("brain", "setPhotoAwareness", {"policy": "AWARE_SILENT", "enabled": True}),
        RpcCase("brain", "setXrHandMode", {"mode": "tracking"}),
    ]


def _safe_unity_cases() -> list[RpcCase]:
    return [
        RpcCase("unity", "animate", {"animation": "idle"}),
        RpcCase("unity", "animate", {"animation": "dance"}),
        RpcCase("unity", "animate", {"animation": "wing_flap"}),
        RpcCase("unity", "animate", {"animation": "head_bob"}),
        RpcCase("unity", "animate", {"animation": "sit"}),
        RpcCase("unity", "animate", {"animation": "sleep"}),
        RpcCase("unity", "animate", {"animation": "perch"}),
    ]


def _motion_cases() -> list[RpcCase]:
    return [
        RpcCase("unity", "flyTo", {"x": 0.0, "y": 0.18, "z": 0.0}),
    ]


def _perch_cases() -> list[RpcCase]:
    return [
        RpcCase(
            "unity",
            "perchToFinger",
            {"require_branch_gesture": False, "timeout_seconds": 2.0},
            expected="ok_or_rejected",
        ),
        RpcCase(
            "unity",
            "returnToView",
            {"timeout_seconds": 2.0},
            expected="ok_or_rejected",
        ),
    ]


def _video_tier_cases() -> list[RpcCase]:
    return [
        RpcCase("unity", "setVideoTier", {"video_tier": "VIDEO_FULL", "reason": "rpc_smoke_matrix"}),
    ]


def _summarize_response(raw: str) -> tuple[bool, str]:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return False, "non_json_response"
    if not isinstance(data, dict):
        return False, f"json_{type(data).__name__}"

    status = str(data.get("status", "") or "")
    reason = str(data.get("reason", "") or "")
    detail = str(data.get("detail") or data.get("message") or "")
    if status == "completed" or status == "ok":
        return True, f"status={status} reason={reason or '-'} detail={detail or '-'}"
    return False, f"status={status or '<missing>'} reason={reason or '-'} detail={detail or '-'}"


async def _call_case(
    room: rtc.Room,
    case: RpcCase,
    target: str,
    response_timeout: float,
) -> tuple[bool, str]:
    payload_json = json.dumps(case.payload, ensure_ascii=False)
    try:
        response = await room.local_participant.perform_rpc(
            destination_identity=target,
            method=case.method,
            payload=payload_json,
            response_timeout=response_timeout,
        )
    except Exception as exc:
        return False, f"TRANSPORT_ERROR {type(exc).__name__}: {exc}"

    ok, summary = _summarize_response(response)
    if case.expected == "ok_or_rejected" and "status=rejected" in summary:
        ok = True
    return ok, f"{summary} raw={response}"


async def _amain(args: argparse.Namespace) -> int:
    _load_env_file(args.env_file)
    identity = args.identity or f"rpc-smoke-matrix-{int(time.time() * 1000)}"
    livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    room_name = args.room or os.getenv("LIVEKIT_ROOM", "parrot-main")
    api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    api_secret = os.getenv("LIVEKIT_API_SECRET", DEFAULT_LOCAL_SECRET)
    urls = _candidate_livekit_urls(livekit_url, args.livekit_url)

    room, used_url = await _connect_room(
        urls=urls,
        identity=identity,
        room_name=room_name,
        api_key=api_key,
        api_secret=api_secret,
    )
    failures = 0
    try:
        brain, unity = await _wait_for_targets(room, args)
        print(f"[rpc_smoke_matrix] connected_url={used_url}")
        print(f"[rpc_smoke_matrix] remotes={_remote_identities(room)}")
        print(f"[rpc_smoke_matrix] brain_target={brain or '<missing>'} unity_target={unity or '<missing>'}")

        cases: list[RpcCase] = []
        if not args.unity_only:
            cases.extend(_safe_brain_cases())
        if not args.brain_only:
            cases.extend(_safe_unity_cases())
            if args.include_motion:
                cases.extend(_motion_cases())
            if args.include_perch:
                cases.extend(_perch_cases())
            if args.include_video_tier:
                cases.extend(_video_tier_cases())

        for case in cases:
            target = brain if case.direction == "brain" else unity
            if not target:
                print(f"[rpc_smoke_matrix] SKIP {case.direction}.{case.method} target_missing")
                failures += 1
                continue

            ok, summary = await _call_case(room, case, target, args.response_timeout)
            mark = "OK" if ok else "FAIL"
            print(f"[rpc_smoke_matrix] {mark} {case.direction}.{case.method} target={target} {summary}")
            if not ok:
                failures += 1
            await asyncio.sleep(max(0.0, args.pause_seconds))

        return 0 if failures == 0 else 2
    finally:
        await room.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a safe LiveKit RPC smoke matrix.")
    parser.add_argument("--identity", default="")
    parser.add_argument("--env-file", default="infra/laptop.env.local")
    parser.add_argument("--livekit-url", default="", help="Override LiveKit URL. Empty tries env URL then localhost fallback.")
    parser.add_argument("--room", default="")
    parser.add_argument("--brain-target", default="")
    parser.add_argument("--unity-target", default="")
    parser.add_argument("--wait-seconds", type=float, default=8.0)
    parser.add_argument("--response-timeout", type=float, default=5.0)
    parser.add_argument("--pause-seconds", type=float, default=0.25)
    parser.add_argument("--brain-only", action="store_true")
    parser.add_argument("--unity-only", action="store_true")
    parser.add_argument("--include-motion", action="store_true")
    parser.add_argument("--include-perch", action="store_true")
    parser.add_argument("--include-video-tier", action="store_true")
    args = parser.parse_args()

    try:
        return asyncio.run(_amain(args))
    except Exception as exc:
        print(f"[rpc_smoke_matrix] ERROR {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
