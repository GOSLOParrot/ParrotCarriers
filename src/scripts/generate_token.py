"""Generate a LiveKit join token for the Unity client.

Usage:
    python src/scripts/generate_token.py                     # defaults
    python src/scripts/generate_token.py --identity unity-phone --room parrot-main
    python src/scripts/generate_token.py --ttl 86400         # 24h token
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parrot.shared.config import ParrotConfig

from livekit.api import AccessToken, VideoGrants


def generate(
    identity: str = "unity-dev",
    room: str | None = None,
    ttl: int = 3600,
) -> str:
    cfg = ParrotConfig()
    room = room or cfg.livekit.room_name

    token = (
        AccessToken(cfg.livekit.api_key, cfg.livekit.api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
            )
        )
        .with_ttl(ttl)
    )
    return token.to_jwt()


def main():
    parser = argparse.ArgumentParser(description="Generate LiveKit join token")
    parser.add_argument("--identity", default="unity-dev", help="Participant identity (default: unity-dev)")
    parser.add_argument("--room", default=None, help="Room name (default: from .env)")
    parser.add_argument("--ttl", type=int, default=3600, help="Token TTL in seconds (default: 3600)")
    args = parser.parse_args()

    jwt = generate(identity=args.identity, room=args.room, ttl=args.ttl)

    print(f"\n  Identity : {args.identity}")
    print(f"  Room     : {args.room or ParrotConfig().livekit.room_name}")
    print(f"  TTL      : {args.ttl}s")
    print(f"\n  Token:\n  {jwt}\n")


if __name__ == "__main__":
    main()
