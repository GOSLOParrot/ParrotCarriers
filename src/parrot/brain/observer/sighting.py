"""Sprint4 Phase 4 W4-5 — sighting observer (实质化).

Authoritative spec:
    - ``architecture/sprint4_phase4_entry_20260430.md §8.4``
    - ``audit_identify_object_no_screenshot_20260420.md §9.5`` (W4-5
      observer 对接)

Subscribes to ``sighting.matched`` / ``sighting.unmatched`` EcpEvents on
the shared :class:`parrot.brain.event_ingest.EcpEventIngest` and runs
**asynchronous** side-effects only — none of these block the
``identify_object`` tool's wall-clock budget (entry doc §8.1 L11).

Boundary contract (entry doc §3.7):
    Observer = "记录" (recording). It MAY:
        * route an event into the IngestRunner (audit-grade Observation)
        * bump L2-B attention / record a sighting timestamp
    It MUST NOT:
        * publish further EcpEvents (sighting.matched is already on the
          wire — looping back would create dedup churn at best, infinite
          fan-out at worst)
        * compute attention thresholds (that is dsg.attention.threshold)
        * write to Graphiti directly (memory.archiver / IngestRunner own
          that path)

Phase 5+ migration target: replace the in-tool ``_upsert_to_l2b`` /
``_ingest_via_runner`` calls inside ``identify_object`` with a thin
"emit sighting.matched and let this observer do everything" pattern.
For Phase 4 W4-5 we keep both paths — the observer is the new home for
async side effects, the in-tool path keeps current behaviour for callers
that haven't migrated.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)


# Observability counters — symmetric with EcpEventPublisher / EcpEventIngest
# so debug HUD and pytest can read the observer's behaviour.
_metrics: dict[str, int] = {
    "matched_received": 0,
    "unmatched_received": 0,
    "archiver_attempts": 0,
    "archiver_successes": 0,
    "l2b_attention_bumps": 0,
}


def get_metrics_snapshot() -> dict[str, int]:
    """Cheap counters dump — for debug HUD / pytest assertions."""
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    """Tests only — drop counters back to zero."""
    for k in _metrics:
        _metrics[k] = 0


# ─── handlers ────────────────────────────────────────────────────────


def _on_sighting_matched(event: EcpEvent) -> None:
    """Async fan-out: archiver + L2-B attention bump.

    Synchronous body schedules an asyncio task because the caller
    (EcpEventIngest._dispatch) is itself synchronous, and archiver /
    L2-B writes are async.
    """
    _metrics["matched_received"] += 1

    payload = event.payload or {}
    candidate_uuid = str(payload.get("candidate_uuid", "") or "")
    label = str(payload.get("label", "") or "")
    description = str(payload.get("description", "") or label)
    category = str(payload.get("category", "") or "")
    match_source = str(payload.get("match_source", "") or "")
    snapshot_uuid = str(payload.get("snapshot_uuid", "") or "")
    confidence_raw = payload.get("confidence", 0.0)
    try:
        confidence = float(confidence_raw)
    except (TypeError, ValueError):
        confidence = 0.0

    if not candidate_uuid:
        # Shouldn't happen — `identify_object._on_match` always sets uuid —
        # but defensive: log and bail rather than crashing the dispatcher.
        logger.debug(
            "[observer.sighting] matched without candidate_uuid (event_id=%s)",
            event.event_id,
        )
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop — can happen in unit tests that drive the ingest
        # directly. Run side effects synchronously via run() in that case
        # would deadlock asyncio; instead just log and skip the async work.
        logger.debug(
            "[observer.sighting] matched skipped async fan-out: no running loop"
        )
        return

    loop.create_task(
        _async_matched_side_effects(
            candidate_uuid=candidate_uuid,
            label=label,
            description=description,
            category=category,
            confidence=confidence,
            match_source=match_source,
            snapshot_uuid=snapshot_uuid,
            event_id=event.event_id,
        )
    )


def _on_sighting_unmatched(event: EcpEvent) -> None:
    """Phase 4 W4-5: log + count only.

    A miss is information for downstream consumers (DSG triggers, future
    attention thresholding) but does NOT promote anything to a node — that
    is GOSLO's call via dispatch_task / save_new on the next turn (audit
    §9.4 option α).
    """
    _metrics["unmatched_received"] += 1
    payload = event.payload or {}
    description = payload.get("description", "")
    n_l0 = len(payload.get("top_l2b_candidates", []) or [])
    n_l1 = len(payload.get("top_graphiti_candidates", []) or [])
    logger.debug(
        "[observer.sighting] unmatched description=%r near=L0:%d/L1:%d (event_id=%s)",
        description, n_l0, n_l1, event.event_id,
    )


# ─── async side effects ─────────────────────────────────────────────


async def _async_matched_side_effects(
    *,
    candidate_uuid: str,
    label: str,
    description: str,
    category: str,
    confidence: float,
    match_source: str,
    snapshot_uuid: str,
    event_id: str,
) -> None:
    """Run archiver + L2-B attention bump for one matched sighting.

    Wrapped in a single try/except per fan-out target so a failure in
    one path (e.g., Graphiti unreachable) does not skip the other.
    """
    # 1) Archiver (audit-grade Observation via IngestRunner).
    _metrics["archiver_attempts"] += 1
    try:
        from parrot.dsg.ingest.runner import get_ingest_runner
        from parrot.dsg.ingest.tool_result_filter import ToolResultFilter

        flt = ToolResultFilter()
        outcome = flt.process_result(
            {
                "label": label or description[:60],
                "graphiti_uuid": candidate_uuid if match_source == "l1_graphiti" else "",
                "description": description,
                "category": category,
                "confidence": confidence,
                "snapshot_uuid": snapshot_uuid,
            }
        )
        if outcome.observations:
            runner = get_ingest_runner()
            if runner is not None:
                await runner.commit_outcome(outcome)
                _metrics["archiver_successes"] += 1
    except Exception:
        logger.debug(
            "[observer.sighting] archiver failed for event_id=%s", event_id,
            exc_info=True,
        )

    # 2) L2-B attention bump — small Δ here is on top of the in-tool
    # _upsert_to_l2b's +0.2 (W4-5 keeps both; Phase 5+ collapses into one
    # path through this observer).
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph

        graph = get_l2b_graph()
        if graph is not None:
            node = graph.get_node(candidate_uuid)
            if node is not None:
                node.attention = min(1.0, node.attention + 0.05)
                _metrics["l2b_attention_bumps"] += 1
    except Exception:
        logger.debug(
            "[observer.sighting] L2-B bump failed for uuid=%s", candidate_uuid,
            exc_info=True,
        )


# ─── registration ───────────────────────────────────────────────────


def register(ingest: EcpEventIngest) -> None:
    """Subscribe to SIGHTING_MATCHED + SIGHTING_UNMATCHED on the given ingest."""
    ingest.subscribe(EcpEventType.SIGHTING_MATCHED, _on_sighting_matched)
    ingest.subscribe(EcpEventType.SIGHTING_UNMATCHED, _on_sighting_unmatched)
    logger.debug(
        "[observer.sighting] Phase 4 W4-5 handlers subscribed "
        "(matched + unmatched)"
    )


__all__ = [
    "get_metrics_snapshot",
    "register",
    "reset_metrics_for_tests",
]
