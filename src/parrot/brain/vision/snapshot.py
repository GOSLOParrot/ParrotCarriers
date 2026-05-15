"""Brain vision helpers: snapshot capture compatibility.

The old Sprint4 helper pulled inline JPEG bytes through a Unity
``captureSnapshot`` LiveKit RPC. Formal Unity no longer exposes that path:
camera-mode photos are owned by ``PhotoController`` and flow as small ECP
metadata plus HTTP/storage assets. ``identify_object`` should be rebuilt on a
separate Intent/SVA path that samples the LiveKit background video stream or a
timestamped frame cache. Keep ``capture_current_frame`` as a non-crashing
compatibility hook for tools that still import it, but do not send image bytes
through RPC here.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parrot.shared.snapshot import SnapshotEnvelope

logger = logging.getLogger(__name__)
_warned_disabled_capture = False


async def capture_current_frame(
    timeout: float = 2.0, max_kb: int = 120, resolution: int = 720
) -> "SnapshotEnvelope | None":
    """Return no frame until the formal photo/SVA capture contract is rebuilt.

    Args are retained for callers/tests from the old ``identify_object`` path.
    The function intentionally does not call Unity RPC, LiveKit ByteStream, or
    any inline image transport.
    """
    del timeout, max_kb, resolution
    global _warned_disabled_capture
    if not _warned_disabled_capture:
        logger.warning(
            "capture_current_frame is disabled: formal Unity uses "
            "PhotoController ECP metadata plus HTTP/storage assets, not "
            "inline image RPC."
        )
        _warned_disabled_capture = True
    await asyncio.sleep(0)
    return None
