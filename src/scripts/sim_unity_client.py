"""Simulate a Unity client in the LiveKit room — for testing Brain Agent without Unity Editor.

This script:
  1. Joins parrot-main room as "unity-sim" (matches _rpc_bridge.py prefix check)
  2. Registers RPC handlers for flyTo / animate (just logs + returns OK)
  3. Optionally publishes microphone audio (set --mic to enable)
  4. Stays alive so Brain Agent can interact with it

Usage:
    python src/scripts/sim_unity_client.py              # join + listen (no mic)
    python src/scripts/sim_unity_client.py --mic        # join + mic + listen

Requires: pip install livekit (the Python client SDK, not livekit-agents)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parrot.shared.config import ParrotConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [sim-unity] %(message)s")
logger = logging.getLogger("sim-unity")

try:
    from livekit import rtc
except ImportError:
    logger.error("Need livekit Python client SDK: pip install livekit")
    sys.exit(1)

from livekit.api import AccessToken, RoomAgentDispatch, VideoGrants
from livekit.protocol.room import RoomConfiguration

AGENT_NAME = "parrot-brain"


def _make_token(identity: str, room: str, cfg: ParrotConfig) -> str:
    room_config = RoomConfiguration(
        agents=[RoomAgentDispatch(agent_name=AGENT_NAME)],
    )
    token = (
        AccessToken(cfg.livekit.api_key, cfg.livekit.api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(VideoGrants(room_join=True, room=room))
        .with_room_config(room_config)
        .with_ttl(timedelta(hours=1))
    )
    return token.to_jwt()


async def _dispatch_agent(cfg: ParrotConfig, room_name: str) -> None:
    """Explicitly dispatch the Brain Agent to the room via LiveKit API."""
    from livekit.api import CreateAgentDispatchRequest, LiveKitAPI

    lk = LiveKitAPI(
        cfg.livekit.url.replace("ws://", "http://").replace("wss://", "https://"),
        cfg.livekit.api_key,
        cfg.livekit.api_secret,
    )
    try:
        dispatch = await lk.agent_dispatch.create_dispatch(
            CreateAgentDispatchRequest(agent_name=AGENT_NAME, room=room_name)
        )
        logger.info("Agent dispatched: %s", dispatch.id)
    finally:
        await lk.aclose()


async def main(use_mic: bool = False):
    cfg = ParrotConfig()
    identity = "unity-sim"
    room_name = cfg.livekit.room_name

    token = _make_token(identity, room_name, cfg)
    logger.info("Identity: %s  Room: %s", identity, room_name)

    room = rtc.Room()

    @room.on("track_subscribed")
    def on_track(track, publication, participant):
        logger.info("Track from %s: %s (%s)", participant.identity, track.sid, track.kind)

    @room.on("participant_connected")
    def on_join(participant):
        logger.info("+ %s joined", participant.identity)

    @room.on("participant_disconnected")
    def on_leave(participant):
        logger.info("- %s left", participant.identity)

    url = cfg.livekit.url
    logger.info("Connecting to %s ...", url)
    await room.connect(url, token)
    logger.info("Connected to room '%s'", room.name)

    @room.local_participant.register_rpc_method("flyTo")
    async def handle_fly_to(data):
        payload = json.loads(data.payload)
        logger.info("RPC flyTo <- %s: %s", data.caller_identity, payload)
        return json.dumps({"status": "ok", "action": "flyTo", "target": payload})

    @room.local_participant.register_rpc_method("animate")
    async def handle_animate(data):
        payload = json.loads(data.payload)
        logger.info("RPC animate <- %s: %s", data.caller_identity, payload)
        return json.dumps({"status": "ok", "action": "animate", "animation": payload.get("animation")})

    logger.info("RPC handlers registered: flyTo, animate")

    has_agent = any(
        p.identity.startswith("agent-") for p in room.remote_participants.values()
    )
    if not has_agent:
        logger.info("No agent in room yet — dispatching %s ...", AGENT_NAME)
        await _dispatch_agent(cfg, room_name)

    logger.info("Waiting for Brain Agent interactions... (Ctrl+C to quit)")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await room.disconnect()
        logger.info("Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate Unity client in LiveKit room")
    parser.add_argument("--mic", action="store_true", help="Publish microphone (not implemented yet)")
    args = parser.parse_args()
    asyncio.run(main(use_mic=args.mic))
