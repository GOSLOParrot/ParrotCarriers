"""Sprint4 Phase 4 W6-7 — F-05 Echo path Brain side (config handler).

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.1 L9``
+ ``architecture/sprint4_phase4_brain_self_audit_20260430.md §3.2 F-05``.

What this module does
---------------------
Subscribes :class:`parrot.brain.event_ingest.EcpEventIngest` to the
``attention.config.echo`` EcpEvent (Unity-source). On receive:

    1. Validate payload shape (5 fields locked in entry doc §8.1 L9 +
       ``bb_schema.py:global/attention_thresholds`` comment).
    2. Write to BB ``global/attention_thresholds`` with writer
       ``brain._rpc_bridge`` (the producer name declared in
       ``bb_schema.py``; this module reuses that string so the producer
       attribution stays consistent without modifying ``_rpc_bridge.py``).

Why a new module instead of folding into ``_rpc_bridge.py``
-----------------------------------------------------------
``_rpc_bridge`` is the **RPC outcome mirror** (writes ``tick/last_rpc_ack``).
The Echo handler is an inbound **DataChannel event consumer** — different
trigger surface (RPC return vs DataChannel inbound), different ownership
boundary (ack mirror vs config sync). Mixing them would muddy the
single-producer-per-key contract that ``_rpc_bridge`` already documents
in its header.

The BB writer string is still ``brain._rpc_bridge`` because that is what
``bb_schema.py`` declares as the producer of
``global/attention_thresholds``; bb_schema is locked in this chat (entry
doc §8.5 #4 + audit constraint). Using the declared producer name here
is the cheap, safe way to satisfy the declared contract from a new
physical file.

Why this is "Brain side" not "Observer side"
--------------------------------------------
``brain.observer.*`` modules per §3.7 are "记录" (event recording → archiver
/ Ref / hint). Config Echo is not an event-of-interest, it's a control-plane
sync: Unity SO value → Brain in-memory cache (BB key). Putting it under
``observer/`` would normalise misuse of that namespace. Top-level
``brain/`` matches the role.

F-05 prerequisite chain status (§8.1 L9 ⚠ note)
-----------------------------------------------
After this module + Unity ``AttentionConfigEchoPublisher`` ship:

    ① Unity SO + EchoPublisher → publish EcpEvent      [LANDED in this chat]
    ② Brain attention_config_handler writes BB         [LANDED in this chat]
    ③ FocusBboxThreshold.__init__ reads BB             [DEFERRED to Brain
                                                        chat — touches
                                                        threshold.py which is
                                                        locked in this chat]

After ① + ②, ``global/attention_thresholds`` has a real producer wired and
can lift the # CANDIDATE marker once entry doc + bb_schema get a follow-up
doc-only chat. Until ③, FocusBboxThreshold still uses the hardcoded
DEFAULTS in threshold.py — Echo writes BB but no consumer reads it yet.
"""

from __future__ import annotations

import logging
from typing import Any

from parrot.brain.event_ingest import EcpEventIngest
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)


# Mirror declared producer in ``bb_schema.py:global/attention_thresholds``.
# Hard-coded so this module does NOT need to import from _rpc_bridge.
_BB_WRITER = "brain._rpc_bridge"
_BB_KEY = "global/attention_thresholds"

# Schema version embedded in the BB payload. Mirrors the C# constant
# ``ParrotAttentionConfig.SchemaVersion``. Bump only on field-set change.
_PAYLOAD_SCHEMA_VERSION = 1

# Locked field names — must match Unity ``ParrotAttentionConfig.ToWireJson``.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "delta_focus",
    "delta_bbox",
    "threshold",
    "target_ttl_s",
    "schema_version",
)


# Observability counters — exposed for test assertions and debug HUD.
_metrics: dict[str, int] = {
    "received": 0,
    "bb_writes": 0,
    "rejected_invalid": 0,
    "rejected_schema_version": 0,
    "bb_write_failed": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    for k in _metrics:
        _metrics[k] = 0


def _on_attention_config_echo(event: EcpEvent) -> None:
    """Validate and persist Echo payload to BB.

    Validation rules (intentionally light — schema is locked, drift is the
    only realistic failure mode):

        * All 5 required fields present.
        * delta_focus / delta_bbox / threshold / target_ttl_s are numeric.
        * threshold > 0 (zero would make accumulator math meaningless;
          Unity SO already clamps but defend on receive).
        * schema_version known. Unknown version → reject + log; do NOT
          silently accept (a future Unity build with v2 must NOT have its
          payload silently truncated to v1 keys).
    """
    _metrics["received"] += 1
    payload: dict[str, Any] = event.payload or {}

    missing = [f for f in _REQUIRED_FIELDS if f not in payload]
    if missing:
        _metrics["rejected_invalid"] += 1
        logger.warning(
            "[attention_config_handler] missing fields %s (event_id=%s)",
            missing, event.event_id,
        )
        return

    schema_version = payload.get("schema_version")
    if schema_version != _PAYLOAD_SCHEMA_VERSION:
        _metrics["rejected_schema_version"] += 1
        logger.warning(
            "[attention_config_handler] schema_version=%r != %d (event_id=%s)",
            schema_version, _PAYLOAD_SCHEMA_VERSION, event.event_id,
        )
        return

    try:
        bb_payload = {
            "delta_focus": float(payload["delta_focus"]),
            "delta_bbox": float(payload["delta_bbox"]),
            "threshold": float(payload["threshold"]),
            "target_ttl_s": float(payload["target_ttl_s"]),
            "schema_version": int(schema_version),
        }
    except (TypeError, ValueError) as exc:
        _metrics["rejected_invalid"] += 1
        logger.warning(
            "[attention_config_handler] non-numeric field (event_id=%s): %s",
            event.event_id, exc,
        )
        return

    if bb_payload["threshold"] <= 0.0:
        _metrics["rejected_invalid"] += 1
        logger.warning(
            "[attention_config_handler] threshold ≤ 0 rejected (event_id=%s)",
            event.event_id,
        )
        return

    try:
        bb = open_bb_client(name="attention_config_handler", writer=_BB_WRITER)
        bb.set(_BB_KEY, bb_payload)
        _metrics["bb_writes"] += 1
        logger.info(
            "[attention_config_handler] BB %s written: Δ_focus=%.3f Δ_bbox=%.3f "
            "threshold=%.3f ttl=%.1fs (event_id=%s)",
            _BB_KEY,
            bb_payload["delta_focus"], bb_payload["delta_bbox"],
            bb_payload["threshold"], bb_payload["target_ttl_s"],
            event.event_id,
        )
    except Exception:
        _metrics["bb_write_failed"] += 1
        logger.exception(
            "[attention_config_handler] BB write failed (event_id=%s)",
            event.event_id,
        )


def register(ingest: EcpEventIngest) -> None:
    """Subscribe the Echo handler on the given ingest.

    Idempotency: subscribing the same callable twice would double-write BB
    on every Echo. Caller (brain.agent boot) is single-shot per session,
    so we don't defensively dedup here — keeping the subscribe API
    matching the other Phase 4 observers (bbox/focus/sighting).
    """
    ingest.subscribe(EcpEventType.ATTENTION_CONFIG_ECHO, _on_attention_config_echo)


__all__ = ["get_metrics_snapshot", "register", "reset_metrics_for_tests"]
