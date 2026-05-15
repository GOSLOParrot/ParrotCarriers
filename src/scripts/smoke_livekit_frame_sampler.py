"""Smoke test the LiveKit frame sampler against a real room.

This is a manual diagnostic for the time-aligned evidence path.  It joins the
configured LiveKit room as a subscriber, attaches ``LiveKitFrameSampler``, waits
for remote video frames, and exits non-zero if no frame is recorded.  It never
prints API secrets or JWTs.

Usage:
    python src/scripts/smoke_livekit_frame_sampler.py --seconds 30 --min-frames 1
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from livekit import rtc
from livekit.api import AccessToken, VideoGrants

from parrot.brain.vision.frame_cache import get_frame_cache
from parrot.brain.vision.livekit_sampler import (
    LiveKitFrameSamplerConfig,
    attach_livekit_frame_sampler,
    read_livekit_frame_sampler_status,
)
from parrot.shared.config import ParrotConfig


def _token(cfg: ParrotConfig, *, identity: str, room: str) -> str:
    return (
        AccessToken(cfg.livekit.api_key, cfg.livekit.api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_subscribe=True,
                can_publish=False,
                can_publish_data=False,
            )
        )
        .with_ttl(timedelta(minutes=10))
        .to_jwt()
    )


async def _run(args: argparse.Namespace) -> int:
    cfg = ParrotConfig()
    room_name = args.room or cfg.livekit.room_name
    identity = args.identity
    token = _token(cfg, identity=identity, room=room_name)
    room = rtc.Room()
    sampler = None

    await room.connect(cfg.livekit.url, token)
    try:
        sampler = attach_livekit_frame_sampler(
            room,
            config=LiveKitFrameSamplerConfig(
                enabled=True,
                fps=args.fps,
                jpeg_quality=args.jpeg_quality,
                max_dimension=args.max_dimension,
                stream_capacity=1,
                include_screenshare=args.include_screenshare,
            ),
        )
        if sampler is None:
            print(json.dumps({"success": False, "message": "sampler_not_started"}, indent=2))
            return 2

        deadline = asyncio.get_running_loop().time() + args.seconds
        while asyncio.get_running_loop().time() < deadline:
            status = sampler.status()
            if int(status.get("recorded_frames") or 0) >= args.min_frames:
                break
            await asyncio.sleep(0.5)

        status = sampler.status()
        frame_cache_status = get_frame_cache().status()
        persisted_status = read_livekit_frame_sampler_status()
        success = int(status.get("recorded_frames") or 0) >= args.min_frames
        print(
            json.dumps(
                {
                    "success": success,
                    "room": room_name,
                    "identity": identity,
                    "sampler": status,
                    "persisted_sampler": persisted_status,
                    "frame_cache": frame_cache_status,
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 0 if success else 2
    finally:
        if sampler is not None:
            await sampler.stop()
        await room.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test LiveKit time-aligned frame sampling.")
    parser.add_argument("--room", default="", help="Room name. Defaults to ParrotConfig livekit room.")
    parser.add_argument("--identity", default="web-frame-sampler-smoke", help="LiveKit participant identity.")
    parser.add_argument("--seconds", type=float, default=20.0, help="How long to wait for frames.")
    parser.add_argument("--min-frames", type=int, default=1, help="Minimum recorded frames required for success.")
    parser.add_argument("--fps", type=float, default=1.0, help="Sampler frames per second.")
    parser.add_argument("--jpeg-quality", type=int, default=78, help="JPEG quality for cached evidence frames.")
    parser.add_argument("--max-dimension", type=int, default=720, help="Largest stored image dimension.")
    parser.add_argument(
        "--no-screenshare",
        dest="include_screenshare",
        action="store_false",
        help="Ignore LiveKit screen-share tracks.",
    )
    parser.set_defaults(include_screenshare=True)
    return asyncio.run(_run(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
