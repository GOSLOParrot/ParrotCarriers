"""Generate a LiveKit join token for the Unity client.

Usage:
    python src/scripts/generate_token.py                     # defaults
    python src/scripts/generate_token.py --identity unity-phone --room parrot-main
    python src/scripts/generate_token.py --ttl 86400         # 24h token
"""

from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parrot.shared.config import ParrotConfig

from livekit.api import AccessToken, VideoGrants

# Brain registers with agent_name="" (unnamed default handler via @server.rtc_session()).
# Do NOT set roomConfig.agents[agentName] here — LiveKit dispatches to unnamed workers
# automatically when a participant joins. Adding a named agentName here causes dispatch
# to fail because no worker with that name exists (Brain uses the default unnamed slot).
# See agent.py brain_entrypoint docstring for the design rationale.


def generate(
    identity: str = "unity-dev",
    room: str | None = None,
    ttl_seconds: int = 3600,
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
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .with_ttl(timedelta(seconds=ttl_seconds))
    )
    return token.to_jwt()


def main():
    parser = argparse.ArgumentParser(description="Generate LiveKit join token")
    parser.add_argument("--identity", default="unity-dev", help="Participant identity (default: unity-dev)")
    parser.add_argument("--room", default=None, help="Room name (default: from .env)")
    parser.add_argument("--ttl", type=int, default=3600, help="Token TTL in seconds (default: 3600)")
    parser.add_argument("-o", "--output", default=None, help="Save token to file (default: unity/ParrotDev/unity_join_token.txt)")
    args = parser.parse_args()

    jwt_token = generate(identity=args.identity, room=args.room, ttl_seconds=args.ttl)
    room_name = args.room or ParrotConfig().livekit.room_name

    print(f"\n  Identity : {args.identity}")
    print(f"  Room     : {room_name}")
    print(f"  TTL      : {args.ttl}s")
    print(f"\n  Token:\n  {jwt_token}\n")

    out_path = args.output or str(Path(__file__).resolve().parents[2] / "unity" / "ParrotDev" / "unity_join_token.txt")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(jwt_token)
    print(f"  Saved to: {out_path}")

    try:
        import subprocess
        subprocess.run(["clip"], input=jwt_token.encode(), check=True)
        print("  Copied to clipboard!")
    except Exception:
        pass

    print()


if __name__ == "__main__":
    main()
