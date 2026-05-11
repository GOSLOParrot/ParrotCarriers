"""Sprint4 Phase 4 — Brain → Unity EcpEvent publisher.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.1``
(L2 / L4 — reliable DataChannel topic ``parrot.ecp.event``) + §8.4 (code
entry).

Mirror of :class:`parrot.brain.event_ingest.EcpEventIngest`: the **outbound**
side of the Brain ↔ Unity event channel. Used by Phase 4 brain-source
event types:

    * ``sighting.matched`` / ``sighting.unmatched``       (W4-5, tool ②)
    * ``attention.threshold.crossed``                     (W6-7, tool ③)
    * ``photo.asset_uploaded``                            (W8, tool ④)
    * ``event.rejected.oversize``                         (always — defensive
      synthesised event already produced by ingest, but consumers may want
      to hear it on the wire too via this publisher; ingest does NOT loop
      back into publisher to avoid feedback)

Why a separate module from ``event_ingest``:
    * Ingest is **synchronous** (LiveKit callback dispatch); publisher is
      **asynchronous** (LiveKit ``publish_data`` is async and may fail on
      transport).
    * Ingest has no LiveKit handle in scope; publisher needs the room +
      local_participant.
    * Splitting also documents the L12 "拆双向" lock without forcing readers
      to scroll past 200 lines of ingest plumbing.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from parrot.shared.ecp_event import (
    TOPIC_ECP_EVENT,
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)

if TYPE_CHECKING:
    from livekit.rtc import Room


logger = logging.getLogger(__name__)


class EcpEventPublisher:
    """Brain-side publisher for the ``parrot.ecp.event`` reliable DataChannel.

    Construction is cheap; binding to a Room happens on first use through the
    held reference. The class is async-aware: :meth:`publish` is an async
    method but offers a fire-and-forget convenience via :meth:`publish_nowait`
    for callers that don't want to await (most synchronous Observer
    callbacks fall in this category — they detected an event and just want
    it on the wire).
    """

    def __init__(self, room: Room) -> None:
        self._room = room
        # Counters mirror EcpEventIngest's introspection surface so debug HUD
        # / metrics consumers can read "send vs receive" symmetrically.
        self.published_count: int = 0
        self.failed_count: int = 0
        self.dropped_no_room_count: int = 0

    # ─── publish ───────────────────────────────────────────────────────

    async def publish(self, event: EcpEvent) -> bool:
        """Send an EcpEvent on the reliable DataChannel. Returns True on
        success, False on transport failure or no live room.

        Caller is expected to have built the event through
        :meth:`EcpEvent.build` so the 8 KB cap is pre-checked. We do not
        re-check here — that is the constructor's responsibility, and a
        re-check would just hide producer bugs in the publisher.
        """
        room = self._room
        if room is None:
            self.dropped_no_room_count += 1
            return False

        local = getattr(room, "local_participant", None)
        if local is None:
            self.dropped_no_room_count += 1
            return False

        wire = event.to_wire_json()
        try:
            await local.publish_data(
                payload=wire,
                reliable=True,
                topic=TOPIC_ECP_EVENT,
            )
        except Exception as exc:
            self.failed_count += 1
            logger.warning(
                "EcpEvent publish failed event_type=%s event_id=%s: %s",
                event.event_type, event.event_id, exc,
            )
            return False

        self.published_count += 1
        return True

    def publish_nowait(self, event: EcpEvent) -> None:
        """Fire-and-forget convenience for synchronous callers.

        Schedules :meth:`publish` on the running event loop. The result is
        discarded (counters still update). MUST only be called from inside a
        thread that has a running asyncio loop — synchronous Observer code
        running inside the LiveKit DataChannel callback satisfies this.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop — drop. We deliberately do NOT spawn a thread
            # here; publishing from outside the agent's event loop is almost
            # always a sign of a deeper bug, and silent magic would hide it.
            self.failed_count += 1
            logger.warning(
                "EcpEvent publish_nowait dropped: no running event loop "
                "(event_type=%s event_id=%s)",
                event.event_type, event.event_id,
            )
            return
        # TODO (audit Round 3 §E, 2026-05-11): pass ``name=`` so this task
        # is debuggable in ``asyncio.all_tasks()`` traces. Cheap improvement,
        # zero behaviour change.
        loop.create_task(self.publish(event))

    # ─── helpers ───────────────────────────────────────────────────────

    def make_brain_event(
        self,
        *,
        event_type: EcpEventType,
        payload: dict[str, Any] | None = None,
        unity_identity: str = "",
        room_id: str = "",
        correlation_id: str = "",
    ) -> EcpEvent:
        """Convenience wrapper around :meth:`EcpEvent.build` that pins
        ``source=brain`` and pulls room_id from the held room when omitted.
        """
        if not room_id and self._room is not None:
            room_id = getattr(self._room, "name", "") or ""
        return EcpEvent.build(
            event_type=event_type,
            source=EcpEventSource.BRAIN,
            payload=payload,
            unity_identity=unity_identity,
            room_id=room_id,
            correlation_id=correlation_id,
        )

    def metrics_snapshot(self) -> dict[str, int]:
        return {
            "published": self.published_count,
            "failed": self.failed_count,
            "dropped_no_room": self.dropped_no_room_count,
        }


# ─── module-level singleton + LiveKit room attach ────────────────────


_publisher_singleton: EcpEventPublisher | None = None


def get_ecp_event_publisher() -> EcpEventPublisher | None:
    """Return the bound singleton, or ``None`` if attach has not run yet.

    Returning None instead of constructing on demand is intentional: a
    publisher without a Room is useless, and silently constructing one
    would hide boot-order bugs.
    """
    return _publisher_singleton


def attach_ecp_event_publisher(room: Room) -> EcpEventPublisher:
    """Bind the publisher singleton to a LiveKit Room.

    Idempotent across reconnects: replacing the room replaces the held
    reference, so old room references die naturally.
    """
    global _publisher_singleton
    _publisher_singleton = EcpEventPublisher(room)
    logger.info("EcpEventPublisher attached — topic %s (room=%s)",
                TOPIC_ECP_EVENT, getattr(room, "name", "?"))
    return _publisher_singleton


def reset_ecp_event_publisher_for_tests() -> None:
    """Drop the singleton — tests only.

    TODO (audit Round 3 §B, 2026-05-11): production code should also drop
    the singleton on ``brain.agent._on_room_disconnected`` so any
    ``publish_nowait`` racing the disconnect doesn't fire against a dead
    Room reference (only inflates ``failed_count``, no correctness bug,
    but spams logs). Add a sibling ``reset_ecp_event_publisher_on_session_end``
    when this becomes a noise problem on real-device smoke.
    """
    global _publisher_singleton
    _publisher_singleton = None


__all__ = [
    "EcpEventPublisher",
    "attach_ecp_event_publisher",
    "get_ecp_event_publisher",
    "reset_ecp_event_publisher_for_tests",
]
