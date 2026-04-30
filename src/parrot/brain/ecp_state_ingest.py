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

# ── observability counters ───────────────────────────────────────────────────
_metrics: dict[str, int] = {
    "received_count": 0,
    "dispatched_count": 0,
    "parse_failures": 0,
    "schema_version_mismatch": 0,
    "bb_write_failures": 0,
    "foreign_topic_ignored": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    """Cheap counters dump — for debug HUD / pytest assertions."""
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    """Reset all counters and BB client — call in pytest setup only."""
    global _bb
    for k in _metrics:
        _metrics[k] = 0
    _bb = None


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

    # 4. Write to BB session/ecp_state (complete dict — consumers pick fields)
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


__all__ = [
    "attach_ecp_state_ingest",
    "get_metrics_snapshot",
    "reset_metrics_for_tests",
]
