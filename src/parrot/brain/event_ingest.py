"""Sprint4 Phase 4 L12 — Python upstream event ingest.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.1`` (L12)
+ §8.4 (code entry table). Wire-up in ``brain.agent`` via
:func:`attach_ecp_event_ingest`.

Architecture
------------
EcpEvent flow on the wire (locked in §8 L4 + §8.2)::

    Unity (publisher) ──► LiveKit reliable DataChannel topic ``parrot.ecp.event``
                                                                │
                                                                ▼
    Brain (this module) ─► dedup by event_id (60s window)
                          ─► schema validate (Pydantic)
                          ─► payload_bytes ≤ 8KB enforcement
                          ─► dispatch to subscribers (observer.event_bus)

This module owns the **upstream** (Unity → Brain) half of the L12 split. The
**downstream** half (Brain → Unity) lives in
``unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventDispatcher.cs``.

Why a separate ingest module instead of folding into ``_rpc_bridge``:
    * ``_rpc_bridge`` owns RPC-shaped payloads and ECP ack mirroring; bolting
      a DataChannel inbound dispatcher onto it would muddy the ack writer's
      single-producer-per-key contract.
    * Phase 4 §8.4 explicitly assigns this code entry to ``brain/event_ingest``
      so the observer package has a single inbound surface to subscribe to.

Phase 4 scope (intentionally minimal)
-------------------------------------
This is the **transport-glue skeleton**. It wires up:
    1. Topic-aware DataChannel handler registration (Phase 4 W3+ wires to a
       real LiveKit Room reference; this module exposes only the
       subscribe/dispatch API + dedup, not the LiveKit bind itself — that's
       owned by ``brain.agent``).
    2. Dedup window keyed on ``event_id`` (60s sliding; entries older than
       window evicted on next ingest).
    3. Schema validation through :class:`parrot.shared.ecp_event.EcpEvent`.
    4. Oversize rejection — emits a synthetic :data:`EcpEventType.EVENT_REJECTED_OVERSIZE`
       so Observers can audit drops.
    5. Subscriber dispatch by ``event_type``.

The actual LiveKit ``Room.DataReceived`` binding is wired up by the agent
bootstrap (Phase 4 W3); this module exposes :meth:`EcpEventIngest.handle_raw`
so the binding is a 3-line hookup with no LiveKit imports here.
"""

from __future__ import annotations

import json
import logging
import time
from collections import OrderedDict
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from parrot.shared.ecp_event import (
    ECP_EVENT_PAYLOAD_LIMIT_BYTES,
    TOPIC_ECP_EVENT,
    EcpEvent,
    EcpEventSource,
    EcpEventType,
)

if TYPE_CHECKING:
    from livekit.rtc import DataPacket, Room


logger = logging.getLogger(__name__)


# Locked in §8.1 L2: 60s sliding window. Tuned conservatively — Reliable
# DataChannel duplicate-delivery on reconnect should never exceed seconds, but
# a generous window costs only memory (one entry per inbound event).
DEDUP_WINDOW_SECONDS: float = 60.0

# Cap dedup memory at this many entries even within the window. Overflow
# evicts oldest first. Sized for ~5Hz inbound average × 60s = 300; 1024
# leaves plenty of headroom for bursts without unbounded growth.
DEDUP_MAX_ENTRIES: int = 1024


SubscriberFn = Callable[[EcpEvent], None]


class EcpEventIngest:
    """In-process upstream EcpEvent receiver, dedup, and dispatcher.

    Single instance per Brain agent process. Not thread-safe by design —
    LiveKit Unity SDK delivers DataChannel callbacks on a single dispatch
    loop; if a future change introduces multi-thread delivery, wrap
    :meth:`handle_raw` with an asyncio.Lock at that boundary instead of
    making the whole class thread-safe (the dispatch fan-out would fight the
    lock otherwise).
    """

    def __init__(
        self,
        *,
        dedup_window_s: float = DEDUP_WINDOW_SECONDS,
        dedup_max_entries: int = DEDUP_MAX_ENTRIES,
    ) -> None:
        self._dedup_window_s = dedup_window_s
        self._dedup_max = dedup_max_entries
        # OrderedDict gives O(1) eviction and chronological iteration without
        # an extra heap. Keys are event_ids; values are arrival times (epoch
        # seconds, monotonic for window math).
        self._seen: OrderedDict[str, float] = OrderedDict()
        # Subscribers keyed by EcpEventType enum value (string). Empty value
        # means "subscribe to all event types" — same semantics as a wildcard
        # but no string magic.
        self._subs: dict[str, list[SubscriberFn]] = {}
        self._wildcard_subs: list[SubscriberFn] = []

        # Observability counters — exposed as plain ints so unit tests can
        # assert without going through a metrics framework. Brain-side
        # telemetry can promote these to a real counter in Phase 5.
        self.received_count: int = 0
        self.dedup_dropped_count: int = 0
        self.oversize_dropped_count: int = 0
        self.malformed_dropped_count: int = 0
        self.dispatched_count: int = 0

    # ─── subscription ────────────────────────────────────────────────

    def subscribe(self, event_type: EcpEventType | None, fn: SubscriberFn) -> None:
        """Register a subscriber. Pass ``event_type=None`` for wildcard.

        Subscribers are called synchronously inside :meth:`handle_raw`. A
        subscriber that raises is logged but does not stop other subscribers —
        Observer-side errors must not poison transport.
        """
        if event_type is None:
            self._wildcard_subs.append(fn)
            return
        self._subs.setdefault(event_type.value, []).append(fn)

    # ─── inbound entry point ────────────────────────────────────────

    def handle_raw(
        self,
        topic: str,
        payload_bytes: bytes,
    ) -> EcpEvent | None:
        """Decode a raw DataChannel frame and dispatch.

        Returns the validated EcpEvent on success (also dispatched), or None
        if the frame was rejected. The return value is mostly for tests; the
        normal consumer path is through :meth:`subscribe`.

        Wire-up from LiveKit (illustrative — actual binding lives in agent
        bootstrap, not here)::

            ingest = EcpEventIngest()
            room.on("data_received", lambda data, participant, kind, topic:
                    ingest.handle_raw(topic, data))
        """
        self.received_count += 1

        if topic != TOPIC_ECP_EVENT:
            # Foreign topic — silently ignore. Other ingest paths (state /
            # health / intent_disconnect) own their own topics; they do not
            # share this dispatcher.
            return None

        # 1) Parse JSON
        try:
            obj = json.loads(payload_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            self.malformed_dropped_count += 1
            logger.warning(
                "EcpEvent malformed JSON on topic=%s: %s (size=%dB)",
                topic, e, len(payload_bytes),
            )
            return None

        # 2) Validate against schema
        try:
            event = EcpEvent.model_validate(obj)
        except ValidationError as e:
            self.malformed_dropped_count += 1
            logger.warning(
                "EcpEvent schema violation on topic=%s: %s",
                topic, e,
            )
            return None

        # 3) Enforce 8KB payload cap (§8.1 L3). We re-encode the payload here
        #    rather than trusting the wire `payload_bytes` field, because the
        #    cap is a **defensive** boundary against a misbehaving / older
        #    Unity client — a producer that forgot to enforce on send must
        #    not be able to bypass it on receive.
        actual_size = len(
            json.dumps(event.payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        )
        if actual_size > ECP_EVENT_PAYLOAD_LIMIT_BYTES:
            self.oversize_dropped_count += 1
            logger.warning(
                "EcpEvent oversize payload event_id=%s event_type=%s size=%dB > %dB cap",
                event.event_id, event.event_type, actual_size, ECP_EVENT_PAYLOAD_LIMIT_BYTES,
            )
            # Synthesize a Brain-source rejection event so observers and
            # downstream metrics see the drop. We do NOT recurse into
            # handle_raw — the synthetic event goes straight to dispatch
            # (and skips dedup, since rejection events have unique ids).
            rejection = EcpEvent.build(
                event_type=EcpEventType.EVENT_REJECTED_OVERSIZE,
                source=EcpEventSource.BRAIN,
                payload={
                    "rejected_event_id": event.event_id,
                    "rejected_event_type": event.event_type,
                    "size_bytes": actual_size,
                    "limit_bytes": ECP_EVENT_PAYLOAD_LIMIT_BYTES,
                },
                correlation_id=event.event_id,
            )
            self._dispatch(rejection)
            return None

        # 4) Dedup
        if self._is_duplicate(event.event_id):
            self.dedup_dropped_count += 1
            return None

        self._record_seen(event.event_id)

        # 5) Dispatch
        self._dispatch(event)
        return event

    # ─── dedup internals ────────────────────────────────────────────

    def _is_duplicate(self, event_id: str) -> bool:
        """O(1) membership check + lazy eviction of stale entries.

        Eviction runs on every check so the dict size is bounded by
        ``window × inbound_rate`` regardless of subscriber behaviour.
        """
        now = time.time()
        cutoff = now - self._dedup_window_s

        # Evict expired entries from the front (OrderedDict iterates in
        # insertion order, which matches arrival-time order since we only
        # ever append). Stop at the first non-expired entry — the rest are
        # younger by construction.
        while self._seen:
            oldest_id, oldest_ts = next(iter(self._seen.items()))
            if oldest_ts >= cutoff:
                break
            self._seen.popitem(last=False)

        return event_id in self._seen

    def _record_seen(self, event_id: str) -> None:
        """Record a fresh event_id, evicting oldest if at capacity."""
        # Capacity-based eviction is a backstop in case the window-based
        # eviction above can't keep up (e.g. a sudden burst). Keep it tight:
        # a one-shot eviction per insert preserves O(1) amortized cost.
        if len(self._seen) >= self._dedup_max:
            self._seen.popitem(last=False)
        self._seen[event_id] = time.time()

    # ─── dispatch ────────────────────────────────────────────────────

    def _dispatch(self, event: EcpEvent) -> None:
        """Fan out to typed subscribers + wildcards. Subscriber errors are
        caught so a single buggy observer cannot poison the rest."""
        self.dispatched_count += 1

        for fn in self._subs.get(str(event.event_type), ()):
            try:
                fn(event)
            except Exception:
                logger.exception(
                    "EcpEvent subscriber %r threw on event_type=%s event_id=%s",
                    fn, event.event_type, event.event_id,
                )

        for fn in self._wildcard_subs:
            try:
                fn(event)
            except Exception:
                logger.exception(
                    "EcpEvent wildcard subscriber %r threw on event_type=%s event_id=%s",
                    fn, event.event_type, event.event_id,
                )

    # ─── debug / introspection ──────────────────────────────────────

    def metrics_snapshot(self) -> dict[str, Any]:
        """Cheap counters dump — for debug HUD / pytest assertions."""
        return {
            "received": self.received_count,
            "dispatched": self.dispatched_count,
            "dedup_dropped": self.dedup_dropped_count,
            "oversize_dropped": self.oversize_dropped_count,
            "malformed_dropped": self.malformed_dropped_count,
            "dedup_window_size": len(self._seen),
        }


# ─── module-level singleton + LiveKit room attach ──────────────────────


_ingest_singleton: EcpEventIngest | None = None


def get_ecp_event_ingest() -> EcpEventIngest:
    """Lazy-construct the process-wide singleton.

    Brain agent boot calls :func:`attach_ecp_event_ingest` (which wraps this
    + binds the LiveKit Room). Tests / other callers that want to register
    subscribers without binding to a Room can call this directly.
    """
    global _ingest_singleton
    if _ingest_singleton is None:
        _ingest_singleton = EcpEventIngest()
    return _ingest_singleton


def reset_ecp_event_ingest_for_tests() -> None:
    """Drop the singleton — tests that need a clean slate call this in setup.

    Production code MUST NOT call this; the singleton is process-wide for a
    reason (subscribers register against it during boot).
    """
    global _ingest_singleton
    _ingest_singleton = None


def attach_ecp_event_ingest(room: Room) -> EcpEventIngest:
    """Wire the EcpEventIngest singleton onto a live LiveKit Room.

    Mirrors the style of :func:`parrot.brain.telemetry_receiver.attach_telemetry_receiver`:
    listens on ``room.on("data_received")`` and routes inbound packets through
    :meth:`EcpEventIngest.handle_raw`. Topic filtering happens inside the
    ingest (foreign topics are silently ignored), so co-existence with the
    telemetry receiver is conflict-free — they share the same SDK callback
    fan-out.

    Returns the singleton so the caller can immediately register Phase 4
    observers / threshold accumulator on it before any data arrives.
    """
    ingest = get_ecp_event_ingest()

    @room.on("data_received")
    def _on_data(packet: DataPacket) -> None:
        topic = getattr(packet, "topic", "") or ""
        # Only act on the EcpEvent topic. Other topics belong to telemetry
        # receiver / future state heartbeat consumer / health envelope
        # consumer; cheap pre-filter avoids decoding for every inbound frame.
        if topic != TOPIC_ECP_EVENT:
            return

        raw = packet.data if isinstance(packet.data, (bytes, bytearray)) else None
        if raw is None:
            # LiveKit Python SDK sometimes hands str; coerce to bytes.
            try:
                raw = (packet.data or "").encode("utf-8") if isinstance(packet.data, str) else b""
            except Exception:
                logger.debug("EcpEvent inbound: cannot coerce packet.data type=%s", type(packet.data))
                return

        try:
            ingest.handle_raw(topic, bytes(raw))
        except Exception:
            # Defensive: handle_raw is supposed to swallow subscriber errors,
            # but if anything escapes (bug in ingest itself), do not poison
            # the LiveKit callback loop — that would silence the telemetry
            # receiver too.
            logger.exception("EcpEventIngest.handle_raw raised on topic=%s", topic)

    logger.info(
        "EcpEventIngest attached — listening on topic %s (dedup_window=%.0fs, max_entries=%d)",
        TOPIC_ECP_EVENT, ingest._dedup_window_s, ingest._dedup_max,
    )
    return ingest


__all__ = [
    "DEDUP_MAX_ENTRIES",
    "DEDUP_WINDOW_SECONDS",
    "EcpEventIngest",
    "SubscriberFn",
    "attach_ecp_event_ingest",
    "get_ecp_event_ingest",
    "reset_ecp_event_ingest_for_tests",
]
