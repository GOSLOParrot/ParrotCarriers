"""Brain vision helpers: Snapshot capture.

Implements `capture_current_frame` via LiveKit RPC to Unity.
Follows S4.A (audit_identify_object_no_screenshot_20260420.md).
"""

from __future__ import annotations

import asyncio
import logging

from livekit.agents import get_job_context

from parrot.brain.tools._rpc_bridge import call_unity_rpc
from parrot.shared.snapshot import (
    CameraPose,
    SnapshotEnvelope,
    SnapshotPayloadKind,
    SnapshotSource,
)

logger = logging.getLogger(__name__)


async def capture_current_frame(
    timeout: float = 2.0, max_kb: int = 120, resolution: int = 720
) -> SnapshotEnvelope | None:
    """Capture the current frame from the AR camera or webcam via RPC.

    Returns:
        SnapshotEnvelope with the inline base64 JPEG payload, or None if failed.
    """
    try:
        room = get_job_context().room
        if not room:
            return None

        # Call the Unity RPC endpoint `captureSnapshot`
        # Using the standard bridge wrapper for LiveKit perform_rpc
        logger.debug("Requesting captureSnapshot RPC (timeout=%s)", timeout)
        
        response_str = await call_unity_rpc(
            method="captureSnapshot",
            payload={"max_kb": max_kb, "resolution": resolution},
            timeout=timeout,
        )

        import json
        resp_data = json.loads(response_str)

        # Expected response format from Unity SnapshotService.cs
        # {
        #   "success": true,
        #   "width": 1280,
        #   "height": 720,
        #   "format": "jpeg",
        #   "b64_data": "...",
        #   "pose": {"px": ..., "py": ..., "pz": ..., "qx": ..., "qy": ..., "qz": ..., "qw": ...}
        # }
        if not resp_data.get("success"):
            logger.warning("captureSnapshot failed: %s", resp_data.get("error", "unknown error"))
            return None

        pose_data = resp_data.get("pose")
        pose = None
        if pose_data:
            pose = CameraPose(**pose_data)

        env = SnapshotEnvelope(
            source=SnapshotSource.UNITY_AR if pose else SnapshotSource.UNITY_WEBCAM,
            width=resp_data.get("width", 720),
            height=resp_data.get("height", 720),
            format=resp_data.get("format", "jpeg"),
            payload_kind=SnapshotPayloadKind.INLINE_JPEG_B64,
            payload_inline_b64=resp_data.get("b64_data", ""),
            camera_pose=pose,
        )
        return env

    except asyncio.TimeoutError:
        logger.warning("captureSnapshot RPC timed out after %ss", timeout)
        return None
    except Exception as e:
        logger.exception("capture_current_frame failed: %s", e)
        return None
