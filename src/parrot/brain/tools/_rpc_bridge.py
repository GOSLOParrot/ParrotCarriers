"""Shared RPC forwarding logic — Tool → LiveKit RPC → Unity client.

All Unity-bound tools (fly_to, animate, etc.) go through this bridge.
"""

from __future__ import annotations

import json
import logging

from livekit.agents import get_job_context
from livekit.agents.llm import ToolError

logger = logging.getLogger(__name__)

UNITY_IDENTITY_PREFIX = "unity"


def _find_unity_participant(room) -> str | None:
    """Find the first Unity client participant in the room."""
    for identity in room.remote_participants:
        if identity.startswith(UNITY_IDENTITY_PREFIX):
            return identity
    return None


async def call_unity_rpc(
    method: str,
    payload: dict,
    timeout: float = 10.0,
) -> str:
    """Forward an RPC call to the Unity client via LiveKit.

    Raises ToolError if Unity is not connected (LLM gets a friendly error).
    """
    room = get_job_context().room
    unity_id = _find_unity_participant(room)

    if not unity_id:
        logger.warning("RPC %s failed: no Unity client in room", method)
        raise ToolError(
            "The AR display isn't connected right now. "
            "I can't move or animate until it joins the room."
        )

    logger.info("RPC → Unity [%s] method=%s", unity_id, method)
    response = await room.local_participant.perform_rpc(
        destination_identity=unity_id,
        method=method,
        payload=json.dumps(payload),
        response_timeout=timeout,
    )
    return response
