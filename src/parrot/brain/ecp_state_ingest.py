"""Sprint4 Phase 4 GAP-1 — EcpState ingest handler.

Authoritative spec:
    - ``architecture/sprint4_phase4_completion_and_final_audit_20260430.md §5.5 Finding B``
      (GAP-1 description + proposal)
    - ``architecture/sprint4_phase4_entry_20260430.md §8.1 L1``
      (EcpState frequency lock: event-driven + 1Hz)
    - ``architecture/sprint4_phase4_completion_and_final_audit_20260430.md §8.2``
      (this chat's implementation scope)

Problem (GAP-1 Finding B)::

    Unity W3.A.3 LifecycleHeartbeatPublisher publishes EcpStateDto JSON
    on topic ``parrot.ecp.state`` (1Hz + event-driven three-state changes).

    Before this module, the Brain side had NO handler for that topic:
        - ``event_ingest`` only routes ``parrot.ecp.event``
        - ``attach_telemetry_receiver`` routes ``parrot.telemetry`` + ``parrot.event``
        - ``parrot.ecp.state`` packets fell into the silent-ignore branch

    Result: BB ``session/ecp_state`` was always None, so selection-C tool
    wrappers in ``tools/_state_context.py`` always read ``active_locks=[]``
    and ``active_command_id=None`` from the ECP side (body/head fed via the
    older telemetry receiver path, but ECP-side data was missing).

Fix::

    This module attaches a ``room.on("data_received")`` callback that:
    1. Filters for topic ``parrot.ecp.state``
    2. JSON-parses the EcpStateDto payload
    3. Writes the full parsed dict to BB ``session/ecp_state``
       (writer = ``brain._rpc_bridge`` per bb_schema.py:178)

    The module does NOT write ``tick/body_state`` or ``tick/head_state``
    because those keys declare ``brain.telemetry_receiver`` as their single
    producer (bb_schema single-producer constraint). Overwriting them here
    would violate the contract and create a dual-writer race with the
    existing telemetry receiver. Readers who want body/head state should
    read from ``tick/body_state`` (telemetry path) OR from
    ``session/ecp_state`` (this path, richer but heavier).

Pattern: mirrors ``attach_telemetry_receiver`` exactly — same attach-function
style, same try/except defensive wrapping, same module-level singleton.
"""

from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING, Any

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp_event import TOPIC_ECP_STATE

if TYPE_CHECKING:
    import py_trees
    from livekit.rtc import DataPacket, Room


logger = logging.getLogger(__name__)


_BB_WRITER = "brain._rpc_bridge"   # bb_schema.py:178 — must stay consistent
_BB_KEY = "session/ecp_state"
_EXPECTED_SCHEMA_VERSION = "ecp.v2.alpha"  # EcpStateDto.schema_version constant

_bb: "py_trees.blackboard.Client | None" = None

# ── sequence_id dedup state (BUG-P3, 2026-05-04) ────────────────────────────
# Tracks the last accepted sequence_id per unity_identity so that duplicate
# packets (e.g. Publisher sends the same 1Hz tick twice during reconnect
# handoff) are dropped before reaching BB.
#
# Design:
#   • key   = unity_identity (str from EcpStateDto)
#   • value = last processed sequence_id (int)
#   • Skip condition: incoming seq <= last AND the gap is small (≤ DEDUP_WINDOW).
#     A large jump backwards means Publisher restarted (boot) — accept it and
#     reset tracking.  Without a boot_id (BUG-U2) we can't distinguish these
#     perfectly, but the window makes the heuristic cheap and low-risk.
#
# NOTE: This does NOT deduplicate across Publisher restarts.  That requires
# BUG-U2 (boot_id field in EcpStateDto).  For now we only handle the simple
# "same packet delivered twice" scenario.
_last_seq: dict[str, int] = {}
_DEDUP_WINDOW = 10  # treat as restart if backwards gap exceeds this value

# ── observability counters ───────────────────────────────────────────────────
_metrics: dict[str, int] = {
    "received_count": 0,
    "dispatched_count": 0,
    "parse_failures": 0,
    "schema_version_mismatch": 0,
    "bb_write_failures": 0,
    "foreign_topic_ignored": 0,
    # BUG-P3: duplicate packets dropped by (identity, sequence_id) dedup
    "duplicate_skipped": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    """Cheap counters dump — for debug HUD / pytest assertions."""
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    """Reset all counters, dedup state and BB client — call in pytest setup only."""
    global _bb
    for k in _metrics:
        _metrics[k] = 0
    _bb = None
    # BUG-P3: also wipe the per-identity dedup tracker so tests are isolated
    _last_seq.clear()


# ── BB client ────────────────────────────────────────────────────────────────


def _ensure_bb() -> "py_trees.blackboard.Client":
    global _bb
    if _bb is None:
        _bb = open_bb_client(name="ecp_state_ingest", writer=_BB_WRITER)
    return _bb


# ── inbound handler ──────────────────────────────────────────────────────────


def _on_ecp_state_packet(data: bytes | str) -> None:
    """Parse one EcpStateDto packet and write BB session/ecp_state.

    Defensive: any exception during parse/BB write is caught and counted;
    it must never propagate to the LiveKit callback loop.
    """
    _metrics["received_count"] += 1

    # 1. Decode bytes → str
    if isinstance(data, (bytes, bytearray)):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as e:
            _metrics["parse_failures"] += 1
            logger.debug("[ecp_state_ingest] UTF-8 decode failed: %s", e)
            return
    else:
        text = data

    # 2. JSON parse
    try:
        obj: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as e:
        _metrics["parse_failures"] += 1
        logger.debug("[ecp_state_ingest] JSON parse failed: %s", e)
        return

    if not isinstance(obj, dict):
        _metrics["parse_failures"] += 1
        logger.debug("[ecp_state_ingest] expected dict, got %s", type(obj).__name__)
        return

    # 3. schema_version check — reject unknown versions to avoid silently writing
    #    an incompatible dict into session/ecp_state (prompt §A.1 spec: skip on mismatch).
    #    When Unity rolls a new schema_version, bump _EXPECTED_SCHEMA_VERSION here too.
    sv = obj.get("schema_version", "")
    if sv != _EXPECTED_SCHEMA_VERSION:
        _metrics["schema_version_mismatch"] += 1
        logger.debug(
            "[ecp_state_ingest] schema_version=%r (expected %r) — skipping to avoid "
            "incompatible write to BB %s",
            sv, _EXPECTED_SCHEMA_VERSION, _BB_KEY,
        )
        return

    # 4. Sequence-id dedup (BUG-P3, 2026-05-04): drop packets whose sequence_id
    #    has already been processed for this unity_identity.  This prevents the
    #    "Publisher sends the same 1Hz tick twice during reconnect" scenario from
    #    producing redundant BB writes.
    #
    #    We skip dedup when either field is absent/zero (cold start or old Unity).
    #    We treat a large backwards jump (> _DEDUP_WINDOW) as a Publisher restart
    #    and reset tracking rather than silently dropping valid new packets.
    unity_identity = str(obj.get("unity_identity", "") or "")
    seq = int(obj.get("sequence_id", 0) or 0)
    if unity_identity and seq:
        last = _last_seq.get(unity_identity, -1)
        if 0 <= last - seq < _DEDUP_WINDOW:
            # seq is equal to, or slightly behind, last accepted — duplicate
            _metrics["duplicate_skipped"] += 1
            logger.debug(
                "[ecp_state_ingest] duplicate seq=%d (last=%d identity=%r) — skipped",
                seq, last, unity_identity,
            )
            return
        # Accept: seq > last, or backwards jump (Publisher restart)
        _last_seq[unity_identity] = seq

    # 5. Write to BB session/ecp_state (complete dict — consumers pick fields)
    #    writer = "brain._rpc_bridge" as declared in bb_schema.py:178
    try:
        bb = _ensure_bb()
        bb.set(_BB_KEY, obj)
        _metrics["dispatched_count"] += 1
        logger.debug(
            "[ecp_state_ingest] BB %s written: body=%s head=%s cognitive=%s "
            "active_cmd=%s locks=%s seq=%s",
            _BB_KEY,
            obj.get("body_state", ""),
            obj.get("head_state", ""),
            obj.get("cognitive_state", ""),
            obj.get("active_command_id", ""),
            obj.get("active_locks", []),
            obj.get("sequence_id", ""),
        )
    except Exception:
        _metrics["bb_write_failures"] += 1
        logger.debug("[ecp_state_ingest] BB write failed", exc_info=True)


# ── room attach (mirror of attach_telemetry_receiver) ────────────────────────


def attach_ecp_state_ingest(room: Room) -> None:
    """Register a DataChannel receive callback on the given LiveKit Room.

    Call this after room.connect() (or inside the rtc_session handler),
    immediately after ``attach_ecp_event_ingest``. Co-existence with
    ``attach_telemetry_receiver`` + ``attach_ecp_event_ingest`` is
    conflict-free — LiveKit SDK fans out ``data_received`` to all registered
    callbacks; topic filtering happens inside each handler.

    GAP-1 fix (Sprint4 Phase 4 audit §5.5 Finding B):
        Without this, Unity W3.A.3 EcpStateDto packets arrive on
        ``parrot.ecp.state`` but no Brain-side handler consumes them, leaving
        BB ``session/ecp_state`` permanently None.
    """
    _ensure_bb()

    @room.on("data_received")
    def _on_data(packet: DataPacket) -> None:
        topic = getattr(packet, "topic", "") or ""
        if topic != TOPIC_ECP_STATE:
            # Foreign topic — owned by other receivers (telemetry / ecp_event /
            # health / intent_disconnect). Silent-ignore.
            _metrics["foreign_topic_ignored"] += 1
            return

        raw = packet.data
        if not raw:
            _metrics["parse_failures"] += 1
            return

        try:
            _on_ecp_state_packet(raw)
        except Exception:
            # Belt-and-suspenders: _on_ecp_state_packet should not raise, but
            # if it does, we must not poison the LiveKit callback loop.
            _metrics["parse_failures"] += 1
            logger.exception("[ecp_state_ingest] unexpected exception in packet handler")

    logger.info(
        "[ecp_state_ingest] GAP-1 handler attached — listening on topic %s "
        "(writer=%s, key=%s)",
        TOPIC_ECP_STATE, _BB_WRITER, _BB_KEY,
    )


# ── disconnect helper (BUG-P4, 2026-05-04) ───────────────────────────────────


def clear_bb_ecp_state() -> None:
    """Write None to BB session/ecp_state.

    Originally written for BUG-P4 (2026-05-04) intending to be called from
    ``brain.agent._on_room_disconnected``. **The wire-up was forgotten** —
    audit (2026-05-11 Round 3, Bug E) found this function had zero callers
    in production code. Use :func:`reset_ecp_state_ingest_on_session_end`
    instead for full session-end cleanup; this function is kept as the
    narrower BB-only primitive for tests / debug scripts.

    Design note: we intentionally write None rather than {} so that
    ``_state_context`` path that reads ``session/ecp_state`` can distinguish
    "never received" from "stale cleared" — both collapse to the same
    ``active_locks=[] / active_command_id=None`` default, but the log entry
    helps debug reconnect timing issues.
    """
    try:
        bb = _ensure_bb()
        bb.set(_BB_KEY, None)
        logger.debug("[ecp_state_ingest] BB %s cleared on disconnect (BUG-P4)", _BB_KEY)
    except Exception:
        logger.debug("[ecp_state_ingest] clear_bb_ecp_state failed", exc_info=True)


def reset_ecp_state_ingest_on_session_end() -> None:
    """Full session-end cleanup: BB clear + per-identity sequence dedup reset.

    FIX (2026-05-11 audit, Round 3, Bugs E + F):
      * **Bug E** — :func:`clear_bb_ecp_state` was declared in its own
        docstring as "called from ``brain.agent._on_room_disconnected``"
        but the call site never landed. ``session/ecp_state`` therefore
        carried stale ECP state from the previous session into the next
        room until the first new packet arrived.
      * **Bug F** — :data:`_last_seq` is a process-global dict keyed by
        ``unity_identity``. Sequence dedup uses ``last - seq < _DEDUP_WINDOW``
        as a duplicate heuristic. After a Unity reconnect with the same
        identity but a fresh sequence (Publisher restart starting at seq=1),
        the next ``_DEDUP_WINDOW`` packets are silently dropped because
        ``last - seq`` falls in the duplicate window. Empirical repro
        (audit Round 3 §F): session 1 ends at seq=5, session 2 publishes
        seq=1..5 → all 5 dropped.

    Called from ``brain.agent._on_room_disconnected`` so the **next** room
    starts with a clean slate without waiting for the BUG-U2 boot_id field
    to land in EcpStateDto.
    """
    clear_bb_ecp_state()
    if _last_seq:
        cleared = len(_last_seq)
        _last_seq.clear()
        logger.info(
            "[ecp_state_ingest] cleared %d per-identity sequence dedup entries "
            "on session end (Bug F fix)",
            cleared,
        )


__all__ = [
    "attach_ecp_state_ingest",
    "clear_bb_ecp_state",
    "get_metrics_snapshot",
    "reset_ecp_state_ingest_on_session_end",
    "reset_metrics_for_tests",
]
