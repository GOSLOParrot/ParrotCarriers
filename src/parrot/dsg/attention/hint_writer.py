"""Phase 4 W6-7 临时 hint writer — **不是** DSG L3 attention 完整模块.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.4``
+ §8.1 L9 + §3.7 Observer/Attention 边界.

What this module does
---------------------
Translates a "threshold crossed" decision (made by
:class:`parrot.dsg.attention.threshold.FocusBboxThreshold`) into an L2-B
attention bump on the **resolved subject** of the AttentionHint:

    AttentionHint.subject_ref → RefBinding → if target_kind == L2B_NODE,
        bump that node's attention by Δ (Δ_focus or Δ_bbox).

If the RefBinding is still UNRESOLVED (which is the **common case** for
Phase 4 W6-7 — BBox/Focus on a not-yet-identified region of the scene),
this writer is a no-op. The L2-B bump only happens once the Ref is
later resolved (via :func:`parrot.brain.refs.resolve_ref`) by an
identify_object hit or a future PhotoEvent ingestion.

Why this lives next to threshold.py instead of in brain/observer/
-----------------------------------------------------------------
The L2-B attention bump is an attention-judgment side-effect tied 1:1
to the threshold crossing, not a generic "I observed an event" fan-out.
Putting it in the same DSG attention package makes the
"threshold decides, hint writer applies" coupling explicit, and keeps
``brain/observer/sighting.py`` from accreting attention math (which
would violate §3.7's Observer/Attention boundary).

Phase 5+ migration path
-----------------------
When DSG L3 注意力模块 lands, this writer is folded into L3's broader
attention bookkeeping (with multi-source arbitration, decay curves,
cross-Episode delta etc.). The public contract surfaced here
(:func:`bump_l2b_for_resolved_ref`) can stay as a compatibility shim
or be deleted — same logic moves into L3.
"""

from __future__ import annotations

import logging
import time

from parrot.shared.ref_binding import RefBinding, RefTargetKind


logger = logging.getLogger(__name__)


# Counters for debug HUD / pytest. Exposed via :func:`metrics_snapshot`.
_metrics: dict[str, int] = {
    "bumps_applied": 0,
    "bumps_skipped_unresolved": 0,
    "bumps_skipped_l2b_unavailable": 0,
    "bumps_skipped_node_missing": 0,
    "bumps_skipped_unsupported_target": 0,
}


def metrics_snapshot() -> dict[str, int]:
    return dict(_metrics)


def reset_metrics_for_tests() -> None:
    for k in _metrics:
        _metrics[k] = 0


def bump_l2b_for_resolved_ref(
    ref: RefBinding,
    *,
    delta: float,
) -> bool:
    """If ``ref`` is resolved to an L2B_NODE, bump that node's attention.

    Returns True iff a bump was actually applied. Any skip path is logged
    + reflected in :func:`metrics_snapshot` so the caller / debug HUD can
    see why no L2-B effect happened.

    ``delta`` is typically ``Δ_focus`` (0.2) for Focus-driven crossings or
    ``Δ_bbox`` (1.0) for BBox-driven crossings — see entry doc §8.1 L9.
    Passing a custom delta is fine; threshold.py is the canonical caller.
    """
    # ``RefBinding.target_kind`` may end up as either the enum member
    # (when constructed via Python) or its string value (when
    # ``model_validate``-d from JSON via ``use_enum_values=True``). Both
    # paths exist in Phase 4 (in-process bind vs round-trip via EcpEvent),
    # so compare via the str-Enum equality (str-Enum members compare
    # equal to their string values) rather than `str(...)` which in
    # Python 3.11 returns `"ClassName.MEMBER"` not the value.
    if ref.target_kind == RefTargetKind.UNRESOLVED or ref.target_kind == RefTargetKind.UNRESOLVED.value:
        _metrics["bumps_skipped_unresolved"] += 1
        logger.debug(
            "[hint_writer] skip — ref_id=%s still UNRESOLVED",
            ref.ref_id,
        )
        return False

    is_l2b = (
        ref.target_kind == RefTargetKind.L2B_NODE
        or ref.target_kind == RefTargetKind.L2B_NODE.value
    )
    if not is_l2b:
        _metrics["bumps_skipped_unsupported_target"] += 1
        logger.debug(
            "[hint_writer] skip — ref_id=%s target_kind=%r not L2B_NODE",
            ref.ref_id, ref.target_kind,
        )
        return False

    if not ref.target_id:
        _metrics["bumps_skipped_unsupported_target"] += 1
        return False

    try:
        from parrot.dsg.l2b_graph import get_l2b_graph

        graph = get_l2b_graph()
    except Exception:
        _metrics["bumps_skipped_l2b_unavailable"] += 1
        logger.debug("[hint_writer] skip — L2-B graph unavailable", exc_info=True)
        return False

    if graph is None:
        _metrics["bumps_skipped_l2b_unavailable"] += 1
        return False

    node = graph.get_node(ref.target_id)
    if node is None:
        _metrics["bumps_skipped_node_missing"] += 1
        logger.debug(
            "[hint_writer] skip — ref_id=%s target_id=%s not in L2-B",
            ref.ref_id, ref.target_id,
        )
        return False

    node.attention = min(1.0, node.attention + delta)
    node.last_attended = time.time()
    _metrics["bumps_applied"] += 1
    logger.debug(
        "[hint_writer] applied +%.2f to L2-B node %s (now attention=%.2f)",
        delta, ref.target_id, node.attention,
    )
    return True


__all__ = [
    "bump_l2b_for_resolved_ref",
    "metrics_snapshot",
    "reset_metrics_for_tests",
]
