"""identify_object — Phase 4 W4-5 staged-flow rewrite.

Authoritative spec:
    - ``architecture/sprint4_phase4_entry_20260430.md §8.1`` (L11 budget)
    - ``audit_identify_object_no_screenshot_20260420.md §9`` (Phase 4 W4-5
      实施口径; supersedes §1.4 / §5 for the current implementation; full
      design preserved there for future stages)

Pipeline (entry doc §8.1 L11 修订, audit §9.5 表):

    LLM 调 identify_object(description, category, action="match")
      │
      ▼
    [Phase 0] time-aligned evidence lookup (≤ 800ms)
        — finds a stored visual sample; failure does not block L0 / L1
      │
      ▼
    [L0] text fast match across L2-B (+ L1.5 hook) (≤ 200ms)
        — pure description simplification + label substring + (future) L1.5
          preloaded node pool. NO image comparison (audit §9.1 用户澄清).
      │
      ├─ hit  → emit sighting.matched + return "I see, this is X"
      ▼
    [L1] Graphiti search (Brain 直连; Nanobot 同步路由 defer Phase 5+) (≤ 800ms)
        — text embedding search across SCENE+USER partitions; first match
          becomes the L1 hit.
      │
      ├─ hit  → emit sighting.matched + return "I think it is X"
      ▼
    [L2] option α — return unknown + top candidates from L0/L1
        — emit sighting.unmatched. GOSLO autonomously decides next step
          (调 dispatch_task / 直接问用户 / 描述). NO web_search inside this
          tool — audit §9.4.

Felt-experience contract (parrot_behavior_rules §0.3):
    Tool returns SYNCHRONOUSLY when GOSLO has its answer (or its "I don't
    know"). No fire-and-forget promises. Each stage's outcome appears in the
    return text so the LLM's next utterance can reflect "I tried L0 then
    L1 then gave up" naturally — see audit §9.3 方案 C.

Felt-experience selection-C (entry doc §8.1 L10):
    Return value is wrapped in :func:`attach_state_header` so the LLM sees
    body/head/cognitive context alongside the identification result.
"""

from __future__ import annotations

import datetime
import json
import logging
import time
import uuid as uuid_lib
from typing import TYPE_CHECKING, Any

from livekit.agents import RunContext, function_tool

from parrot.brain.event_publisher import get_ecp_event_publisher
from parrot.brain.tools._budget import with_budget
from parrot.brain.tools._state_context import attach_state_header
from parrot.brain.vision.evidence import resolve_identify_evidence
from parrot.brain.vision.evidence_image import describe_evidence_sample
from parrot.brain.vision.same_object_resolver import resolve_same_object
from parrot.shared.ecp_event import EcpEventType

if TYPE_CHECKING:
    from parrot.brain.vision.evidence import TimeAlignedSampleRef

logger = logging.getLogger(__name__)


# Phase 4 W4-5 budget (entry doc §8.1 L11 修订 + audit §9.6).
# Budget redistributed because L0 no longer does visual_match.
_BUDGET_CAPTURE_S = 0.8
_BUDGET_VLM_DESCRIBE_S = 0.9
_BUDGET_SAME_OBJECT_S = 1.2
_BUDGET_L0_TEXT_S = 0.2
_BUDGET_L1_GRAPHITI_S = 0.8
# same-object may spend an extra bounded VLM compare before L0/L1; keep the
# match path synchronous so GOSLO can voice a real result instead of a promise.

# Confidence floor on L0 text match. Below this we skip the candidate to
# reduce false positives from short common substrings ("cup" hitting "cupcake").
_L0_MIN_CONFIDENCE = 0.5

# Maximum L0 candidates we surface in stage info / unmatched payload. Keeps
# the LLM-facing return text small.
_L0_TOP_K = 3
_L1_TOP_K = 5


@function_tool()
async def identify_object(
    context: RunContext,
    description: str,
    category: str = "",
    action: str = "match",
    evidence_id: str = "",
    bbox_ref_id: str = "",
    focus_ref_id: str = "",
    target_time_ms: int = 0,
    photo_id: str = "",
    object_ref_id: str = "",
) -> str:
    """Identify, match, or save an object you see in the camera feed.

    Use this when:
      - The user asks "what is this?" or "do you recognize this?"
        (action='match' — default)
      - You spot something new and want to remember it (action='save_new')

    Args:
        description: Visual description (e.g., "blue ceramic mug",
            "silver laptop", "small brown bottle with white label").
        category: Optional category hint (e.g., "container", "electronics",
            "furniture", "medicine").
        action: 'match' (default — staged L0 → L1 → unknown) or
            'save_new' (remember as new object).

    Note (Phase 4 W4-5 audit §9.4): action='deep_search' has been REMOVED.
    If you want to delegate research to the maid, call ``dispatch_task``
    explicitly — that gives you the right "我派出去查了" felt experience
    instead of pretending the result is in this tool's reply.
    """
    if action == "save_new":
        return attach_state_header(
            await _save_new_object(
                description,
                category,
                evidence_id=evidence_id,
                bbox_ref_id=bbox_ref_id,
                focus_ref_id=focus_ref_id,
                target_time_ms=target_time_ms,
                photo_id=photo_id,
                object_ref_id=object_ref_id,
            )
        )
    if action == "deep_search":
        # Defensive: explicit removal banner per audit §3.4 / §9.4. We do
        # NOT silently route through dispatch_task — that would conceal the
        # API change from anyone reading the Soul prompt history.
        return attach_state_header(
            "action='deep_search' is no longer supported. "
            "Call dispatch_task(...) directly if you want to delegate "
            "research to the maid (background task) — that gives you the "
            "correct '我派出去查了' felt experience."
        )
    # action == 'match' is the default; fall through.
    return attach_state_header(
        await _match_staged(
            description,
            category,
            evidence_id=evidence_id,
            bbox_ref_id=bbox_ref_id,
            focus_ref_id=focus_ref_id,
            target_time_ms=target_time_ms,
            photo_id=photo_id,
            object_ref_id=object_ref_id,
        )
    )


# ─── orchestrator ────────────────────────────────────────────────────


async def _match_staged(
    description: str,
    category: str,
    *,
    evidence_id: str = "",
    bbox_ref_id: str = "",
    focus_ref_id: str = "",
    target_time_ms: int = 0,
    photo_id: str = "",
    object_ref_id: str = "",
) -> str:
    """Phase 0 + L0 + L1 + L2 staged orchestrator.

    Returns a single LLM-facing string with stage info inline so the LLM's
    next utterance can voice the journey ("hmm let me see... oh it's X").
    """
    stages: list[str] = []
    snapshot_id = ""
    evidence_sample: "TimeAlignedSampleRef | None" = None
    search_description = description

    # Phase 0: time-aligned evidence lookup. We await first because L0/L1
    # side effects should carry the selected evidence id when one exists.
    # Formal design note: this must not revive the old Unity snapshot RPC.
    # identify_object is a GOSLO Intent-layer behavior; visual evidence should
    # come from the LiveKit background video stream or an SVA frame cache using
    # a timestamp/ref, then feed L2-B/Graphiti as storage-backed evidence.
    # Missing evidence records a pending request instead of calling Unity.
    evidence_seg = await with_budget(
        resolve_identify_evidence(
            evidence_id=evidence_id,
            bbox_ref_id=bbox_ref_id,
            focus_ref_id=focus_ref_id,
            target_time_ms=target_time_ms,
            description=description,
        ),
        timeout_s=_BUDGET_CAPTURE_S + 0.1,  # +100ms cushion for the wrapper
        segment="visual_evidence_lookup",
    )
    if evidence_seg.ok and evidence_seg.value is not None:
        evidence_sample = evidence_seg.value
        # The evidence id is the sighting correlation id until CORE-012
        # promotes a shared top-level field for visual evidence.
        snapshot_id = evidence_sample.evidence_id
        asset_label = evidence_sample.asset_uri or evidence_sample.asset_path or "asset"
        stages.append(
            f"[evidence] ready kind={evidence_sample.kind} id={snapshot_id} "
            f"asset={asset_label} ({evidence_seg.elapsed_ms}ms)"
        )
    else:
        # Missing visual evidence does not block L0 / L1. The resolver records
        # a pending request; frame workers or HTTP uploads can satisfy it later.
        reason = evidence_seg.error or "pending"
        stages.append(f"[evidence] pending: {reason} ({evidence_seg.elapsed_ms}ms)")

    # WEB-015.6: use only storage-backed images/crops as VLM input. This keeps
    # image bytes out of ECP/RPC and prevents the old snapshot RPC path from
    # sneaking back into identify_object.
    if evidence_sample is not None and evidence_sample.asset_path:
        vlm_seg = await with_budget(
            describe_evidence_sample(evidence_sample),
            timeout_s=_BUDGET_VLM_DESCRIBE_S,
            segment="VLM_describe_evidence",
        )
        if vlm_seg.ok and vlm_seg.value:
            visual_hint = _compact_text(str(vlm_seg.value), 160)
            search_description = _merge_visual_hint(description, visual_hint)
            stages.append(f"[VLM] image detail: {visual_hint} ({vlm_seg.elapsed_ms}ms)")
        elif vlm_seg.error:
            stages.append(f"[VLM] skipped: {vlm_seg.error} ({vlm_seg.elapsed_ms}ms)")

    if evidence_sample is not None:
        resolver_seg = await with_budget(
            resolve_same_object(
                evidence_sample=evidence_sample,
                description=search_description,
                category=category,
                photo_id=photo_id,
                object_ref_id=object_ref_id,
            ),
            timeout_s=_BUDGET_SAME_OBJECT_S + 0.1,
            segment="same_object_resolver",
        )
        if resolver_seg.ok and resolver_seg.value:
            resolver_report = resolver_seg.value
            resolver_status = str(resolver_report.get("status") or "")
            best_uuid = str(resolver_report.get("best_object_uuid") or "")
            best_conf = float(resolver_report.get("best_confidence") or 0.0)
            stages.append(
                f"[same-object] {resolver_status} best={best_uuid or '(none)'} "
                f"conf={best_conf:.2f} report={resolver_report.get('report_path', '')} "
                f"({resolver_seg.elapsed_ms}ms)"
            )
            if resolver_status == "matched" and best_uuid:
                label = _resolver_label(resolver_report, best_uuid) or best_uuid
                await _on_match(
                    source="same_object_resolver",
                    uuid=best_uuid,
                    label=label,
                    description=search_description,
                    category=category,
                    confidence=best_conf,
                    snapshot_id=snapshot_id,
                    evidence_sample=evidence_sample,
                )
                return _format_match_reply(
                    stages=stages,
                    source="same-object",
                    label=label,
                    uuid=best_uuid,
                    confidence=best_conf,
                )
        else:
            stages.append(
                f"[same-object] skipped: {resolver_seg.error or 'pending'} "
                f"({resolver_seg.elapsed_ms}ms)"
            )

    # ─── L0: text fast match across L2-B (+ L1.5 hook)
    l0_seg = await with_budget(
        _l0_text_fast_match(search_description, category),
        timeout_s=_BUDGET_L0_TEXT_S + 0.05,
        segment="L0_text",
    )
    l0_candidates: list[tuple[str, str, float]] = (
        l0_seg.value if (l0_seg.ok and l0_seg.value is not None) else []
    )

    if l0_candidates:
        best_uuid, best_label, best_conf = l0_candidates[0]
        if best_conf >= _L0_MIN_CONFIDENCE:
            stages.append(
                f"[L0] matched '{best_label}' (conf={best_conf:.2f}, "
                f"uuid={best_uuid}, {l0_seg.elapsed_ms}ms)"
            )
            await _on_match(
                source="l0_text",
                uuid=best_uuid,
                label=best_label,
                description=search_description,
                category=category,
                confidence=best_conf,
                snapshot_id=snapshot_id,
                evidence_sample=evidence_sample,
            )
            return _format_match_reply(
                stages=stages,
                source="L0",
                label=best_label,
                uuid=best_uuid,
                confidence=best_conf,
            )
        stages.append(
            f"[L0] best below threshold: '{best_label}' conf={best_conf:.2f} "
            f"< {_L0_MIN_CONFIDENCE} ({l0_seg.elapsed_ms}ms)"
        )
    else:
        stages.append(
            f"[L0] no L2-B match ({l0_seg.elapsed_ms}ms"
            f"{', timeout' if l0_seg.error == 'timeout' else ''})"
        )

    # ─── L1: Graphiti search
    l1_seg = await with_budget(
        _l1_graphiti_search(search_description, category),
        timeout_s=_BUDGET_L1_GRAPHITI_S + 0.1,
        segment="L1_graphiti",
    )
    l1_results: list[dict[str, Any]] = (
        l1_seg.value if (l1_seg.ok and l1_seg.value is not None) else []
    )

    if l1_results:
        best = l1_results[0]
        l1_uuid = best.get("uuid", "") or ""
        l1_label = best.get("label", "") or best.get("fact", "")[:60] or "(unknown)"
        stages.append(
            f"[L1] Graphiti found {len(l1_results)} candidates, "
            f"top='{l1_label}' uuid={l1_uuid} ({l1_seg.elapsed_ms}ms)"
        )
        if l1_uuid:
            # Feed the L1 hit through the same _on_match path so L2-B
            # attention bumps + sighting event happen consistently.
            await _on_match(
                source="l1_graphiti",
                uuid=l1_uuid,
                label=l1_label,
                description=search_description,
                category=category,
                confidence=0.7,  # nominal — Graphiti search lacks numeric score
                snapshot_id=snapshot_id,
                evidence_sample=evidence_sample,
            )
            return _format_match_reply(
                stages=stages,
                source="L1",
                label=l1_label,
                uuid=l1_uuid,
                confidence=0.7,
            )

    stages.append(
        f"[L1] no Graphiti match ({l1_seg.elapsed_ms}ms"
        f"{', timeout' if l1_seg.error == 'timeout' else ''})"
    )

    # ─── L2 option α: return unknown + top candidates, defer to GOSLO
    await _on_unmatched(
        description=description,
        category=category,
        snapshot_id=snapshot_id,
        evidence_sample=evidence_sample,
        l0_candidates=l0_candidates,
        l1_results=l1_results,
    )
    return _format_unknown_reply(
        stages=stages,
        description=description,
        snapshot_id=snapshot_id,
        evidence_sample=evidence_sample,
        l0_candidates=l0_candidates,
        l1_results=l1_results,
    )


# ─── L0: text fast match across L2-B (+ L1.5 hook) ────────────────────


async def _l0_text_fast_match(
    description: str,
    category: str,
) -> list[tuple[str, str, float]]:
    """Fast text match across L2-B nodes + L1.5 preloaded pool (hook).

    Returns ranked candidates as ``[(uuid, label, confidence), ...]``,
    sorted by confidence descending. Empty list = miss.

    Confidence calculation (Phase 4 W4-5 starter):
        1.0 if description == node.label (case-insensitive equality)
        0.8 if description appears as substring of node.label OR
            node.label appears as substring of description (and either
            length ≥ 3 to avoid trivial matches)
        +0.1 bonus if category provided AND matches node.category
        capped at 1.0

    L1.5 hook (audit §9.1): future preloaded "to-be-discovered" node pool
    should contribute candidates here. For Phase 4 we only call into the
    existing L2-B graph; the hook is a TODO marker.
    """
    candidates: list[tuple[str, str, float]] = []
    desc_lower = description.strip().lower()
    category_lower = category.strip().lower()
    if not desc_lower:
        return candidates

    try:
        from parrot.dsg.l2b_graph import get_l2b_graph
        from parrot.dsg.l2b_types import ConfirmationStatus

        graph = get_l2b_graph()
        if graph is None or graph.node_count() == 0:
            return candidates

        for node in graph.all_nodes():
            if node.confirmation == ConfirmationStatus.GHOST:
                continue
            label_lower = node.label.lower()
            score = 0.0
            if not label_lower:
                continue
            if desc_lower == label_lower:
                score = 1.0
            elif desc_lower in label_lower and len(desc_lower) >= 3:
                score = 0.8
            elif label_lower in desc_lower and len(label_lower) >= 3:
                score = 0.8

            # Description simplification fallback — try matching the description
            # words against the node description text for richer recall.
            if score == 0.0 and node.description:
                node_desc_lower = node.description.lower()
                if desc_lower in node_desc_lower:
                    score = 0.6

            if score == 0.0:
                continue

            if category_lower and node.category and category_lower == node.category.lower():
                score = min(1.0, score + 0.1)

            # SemanticNode.evidence_score is float ≥ 0.0 by design; no floor
            # gate needed here. Phase 5+ scoring tune may add a positive
            # threshold (e.g. < 0.3 → skip) — see audit §9.1 hook.

            candidates.append((node.uuid, node.label, score))

        candidates.sort(key=lambda t: t[2], reverse=True)

        # TODO(L1.5): once L2-B 完善 lands the "to-be-discovered" preloaded
        # node pool, blend its candidates into the same ranking here. The
        # public contract (return shape) does not change.

    except Exception:
        logger.debug("identify_object: L0 text match unavailable", exc_info=True)

    return candidates[:_L0_TOP_K]


# ─── L1: Graphiti search ──────────────────────────────────────────────


async def _l1_graphiti_search(description: str, category: str) -> list[dict[str, Any]]:
    """Direct Brain → Graphiti search (Phase 4 simplification per audit §9.2).

    Phase 5+ migration target: route through Nanobot for sync wait + MCP
    fusion. Felt experience is identical (sync await with same budget),
    so the LLM-facing contract does not change at migration time.

    Returns ``[{uuid, fact, label}, ...]`` — empty list = no hit.
    """
    results: list[dict[str, Any]] = []
    try:
        import re

        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()
        query = f"object: {description}"
        if category:
            query += f" category: {category}"

        graphiti_hits = await g.search(
            query=query,
            group_ids=[PARTITIONS.SCENE, PARTITIONS.USER],
            num_results=_L1_TOP_K,
        )
        if not graphiti_hits:
            return results

        uuid_re = re.compile(r"\(uuid=([^)]+)\)")
        for hit in graphiti_hits:
            fact = getattr(hit, "fact", None) or getattr(hit, "text", str(hit))
            m = uuid_re.search(fact)
            uuid_str = m.group(1) if m else ""
            clean_fact = uuid_re.sub("", fact).strip()
            results.append({
                "uuid": uuid_str,
                "fact": clean_fact,
                # No native label in Graphiti search results — synthesize
                # from the leading words of the fact for stage info.
                "label": clean_fact.split(":", 1)[-1].strip()[:60] if ":" in clean_fact else clean_fact[:60],
            })

    except Exception:
        logger.debug("identify_object: Graphiti search unavailable", exc_info=True)

    return results


# ─── on-match / on-unmatched side effects ─────────────────────────────


async def _on_match(
    *,
    source: str,
    uuid: str,
    label: str,
    description: str,
    category: str,
    confidence: float,
    snapshot_id: str,
    evidence_sample: "TimeAlignedSampleRef | None" = None,
) -> None:
    """Synchronous L2-B attention bump + async sighting.matched event.

    L2-B attention update is sync because it is in-process and < 1ms.
    Sighting event publish is async (publish_nowait) so transport latency
    cannot extend the tool's wall-clock past the budget.
    """
    await _upsert_to_l2b(
        uuid=uuid,
        description=description,
        category=category,
        from_graphiti=(source == "l1_graphiti"),
        graphiti_uuid=uuid if source == "l1_graphiti" else "",
    )

    publisher = get_ecp_event_publisher()
    if publisher is not None:
        try:
            evidence_payload = _evidence_payload(evidence_sample)
            event = publisher.make_brain_event(
                event_type=EcpEventType.SIGHTING_MATCHED,
                payload={
                    "candidate_uuid": uuid,
                    "label": label,
                    "confidence": confidence,
                    "snapshot_uuid": snapshot_id,
                    "evidence_id": evidence_payload.get("evidence_id", ""),
                    "evidence_asset_uri": evidence_payload.get("asset_uri", ""),
                    "evidence_asset_path": evidence_payload.get("asset_path", ""),
                    "match_source": source,
                    "category": category,
                },
                correlation_id=snapshot_id or uuid,
            )
            publisher.publish_nowait(event)
        except Exception:
            logger.debug("identify_object: sighting.matched publish failed", exc_info=True)
    _record_candidate_object_discovery(
        object_uuid=uuid,
        evidence_sample=evidence_sample,
        description=description,
        category=category,
        match_source=source,
        match_confidence=confidence,
    )


async def _on_unmatched(
    *,
    description: str,
    category: str,
    snapshot_id: str,
    l0_candidates: list[tuple[str, str, float]],
    l1_results: list[dict[str, Any]],
    evidence_sample: "TimeAlignedSampleRef | None" = None,
) -> None:
    """Async sighting.unmatched event. No L2-B / archiver side effects.

    A miss is information for downstream consumers (DSG triggers, future
    attention thresholding) but does NOT promote anything to a node — that
    is GOSLO's call via dispatch_task / save_new on the next turn.
    """
    publisher = get_ecp_event_publisher()
    if publisher is None:
        return
    try:
        evidence_payload = _evidence_payload(evidence_sample)
        event = publisher.make_brain_event(
            event_type=EcpEventType.SIGHTING_UNMATCHED,
            payload={
                "description": description,
                "category": category,
                "snapshot_uuid": snapshot_id,
                "evidence_id": evidence_payload.get("evidence_id", ""),
                "evidence_asset_uri": evidence_payload.get("asset_uri", ""),
                "evidence_asset_path": evidence_payload.get("asset_path", ""),
                "top_l2b_candidates": [
                    {"uuid": uid, "label": lbl, "score": score}
                    for uid, lbl, score in l0_candidates
                ],
                "top_graphiti_candidates": [
                    {"uuid": r.get("uuid", ""), "fact": r.get("fact", "")}
                    for r in l1_results
                ],
            },
            correlation_id=snapshot_id,
        )
        publisher.publish_nowait(event)
    except Exception:
        logger.debug("identify_object: sighting.unmatched publish failed", exc_info=True)


# ─── L2-B upsert helper (kept from prior implementation) ──────────────


async def _upsert_to_l2b(
    uuid: str,
    description: str,
    category: str,
    *,
    from_graphiti: bool = False,
    graphiti_uuid: str = "",
) -> None:
    """Create or update a node in L2-B working memory.

    Phase 4 W4-5 keeps the existing attention bump (audit §9.5 row
    "L2-B 候选权重 +Δ_match"); W6-7 will route through
    ``dsg.attention.hint_writer`` once threshold accumulator is fully
    wired.
    """
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph
        from parrot.dsg.l2b_types import (
            ConfirmationStatus,
            NodeKind,
            Salience,
            SemanticNode,
        )

        graph = get_l2b_graph()
        existing = graph.get_node(uuid)
        if existing:
            existing.attention = min(1.0, existing.attention + 0.2)
            existing.last_seen_this_session = time.time()
            existing.interaction_count += 1
            if from_graphiti and existing.confirmation == ConfirmationStatus.EXPECTED:
                existing.confirmation = ConfirmationStatus.CONFIRMED
                existing.evidence_score = max(existing.evidence_score, 0.6)
            return

        node = SemanticNode(
            uuid=uuid,
            kind=NodeKind.OBJECT,
            label=description[:60],
            graphiti_uuid=graphiti_uuid,
            category=category,
            description=description,
            confirmation=(
                ConfirmationStatus.CONFIRMED if from_graphiti
                else ConfirmationStatus.TENTATIVE
            ),
            evidence_score=0.5 if from_graphiti else 0.1,
            attention=0.7,
            salience=Salience.ACTIVE,
        )
        graph.upsert_node(node)
        graph.assign_node_to_current_episode(uuid)
    except Exception:
        logger.debug("identify_object: L2-B upsert skipped (graph unavailable)")


# ─── save_new branch (preserved from prior implementation) ────────────


async def _save_new_object(
    description: str,
    category: str,
    *,
    evidence_id: str = "",
    bbox_ref_id: str = "",
    focus_ref_id: str = "",
    target_time_ms: int = 0,
    photo_id: str = "",
    object_ref_id: str = "",
) -> str:
    """Save a newly discovered object to Graphiti + L2-B + emit trigger event."""
    try:
        obj_uuid = f"obj_{uuid_lib.uuid4().hex}"
        evidence_sample: "TimeAlignedSampleRef | None" = None
        evidence_seg = await with_budget(
            resolve_identify_evidence(
                evidence_id=evidence_id,
                bbox_ref_id=bbox_ref_id,
                focus_ref_id=focus_ref_id,
                target_time_ms=target_time_ms,
                description=description,
                request_source="identify_object.save_new",
            ),
            timeout_s=_BUDGET_CAPTURE_S + 0.1,
            segment="visual_evidence_lookup_save_new",
        )
        if evidence_seg.ok and evidence_seg.value is not None:
            evidence_sample = evidence_seg.value

        text_parts = [f"New object discovered (uuid={obj_uuid}): {description}"]
        if category:
            text_parts.append(f"  category: {category}")
        text_parts.append(f"  discovered_at: {time.strftime('%Y-%m-%d %H:%M')}")
        text_parts.append("  status: newly_discovered, pending_enrichment")
        text = "\n".join(text_parts)

        try:
            from graphiti_core.nodes import EpisodeType

            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

            g = await get_graphiti()
            await g.add_episode(
                name=f"gemini_discovery_{obj_uuid}",
                episode_body=text,
                source=EpisodeType.text,
                source_description=f"gemini_discovery:{obj_uuid}",
                reference_time=datetime.datetime.now(datetime.timezone.utc),
                group_id=PARTITIONS.SCENE,
            )
        except Exception:
            logger.debug("identify_object: Graphiti save_new episode skipped", exc_info=True)

        await _upsert_to_l2b(obj_uuid, description, category)
        accepted_sample = _accept_new_object_sample(
            object_uuid=obj_uuid,
            description=description,
            category=category,
            evidence_sample=evidence_sample,
            photo_uuid=photo_id,
            object_ref_id=object_ref_id,
        )
        await _ingest_via_runner(
            label=description[:60],
            description=description,
            category=category,
            graphiti_uuid=obj_uuid,
            confidence=0.9,
        )
        await _emit_trigger_event("new_object", {
            "uuid": obj_uuid,
            "description": description,
            "category": category,
        })

        logger.info("identify_object: saved new object %s: %s", obj_uuid, description)
        sample_note = ""
        sample = accepted_sample.get("sample", {}) if accepted_sample else {}
        if sample.get("sample_uuid"):
            sample_note = (
                f" ObjectSample={sample.get('sample_uuid')} "
                f"crop={sample.get('crop_path') or '(none)'}."
            )
        return (
            f"Saved new object '{description}' (id: {obj_uuid}). "
            "I'll remember it from now on."
            f"{sample_note} "
            "If you want me to research what this is, call dispatch_task with "
            "task_type='research'."
        )

    except Exception:
        logger.exception("identify_object._save_new failed")
        return "I noticed something new but couldn't save it to my memory right now."


def _accept_new_object_sample(
    *,
    object_uuid: str,
    description: str,
    category: str,
    evidence_sample: "TimeAlignedSampleRef | None",
    photo_uuid: str,
    object_ref_id: str,
) -> dict[str, Any]:
    try:
        from parrot.brain.vision.object_discovery import accept_new_object_from_evidence

        return accept_new_object_from_evidence(
            object_uuid=object_uuid,
            description=description,
            category=category,
            evidence_sample=evidence_sample,
            photo_uuid=photo_uuid,
            object_ref_id=object_ref_id,
            match_source="user_confirmed",
            match_confidence=0.9,
        )
    except Exception:
        logger.debug("identify_object: accepted sample write skipped", exc_info=True)
        return {}


def _record_candidate_object_discovery(
    *,
    object_uuid: str,
    evidence_sample: "TimeAlignedSampleRef | None",
    description: str,
    category: str,
    match_source: str,
    match_confidence: float,
) -> None:
    try:
        from parrot.brain.vision.object_discovery import record_candidate_match_from_evidence

        record_candidate_match_from_evidence(
            object_uuid=object_uuid,
            evidence_sample=evidence_sample,
            description=description,
            category=category,
            match_source=match_source,
            match_confidence=match_confidence,
        )
    except Exception:
        logger.debug("identify_object: candidate sample write skipped", exc_info=True)


# ─── archiver / trigger helpers (lifted from prior implementation) ────


async def _ingest_via_runner(
    label: str,
    description: str,
    category: str,
    graphiti_uuid: str = "",
    confidence: float = 0.9,
) -> None:
    """Fire ToolResultFilter → IngestRunner as an audit side-channel."""
    try:
        from parrot.dsg.ingest.runner import get_ingest_runner
        from parrot.dsg.ingest.tool_result_filter import ToolResultFilter

        flt = ToolResultFilter()
        outcome = flt.process_result(
            {
                "label": label,
                "graphiti_uuid": graphiti_uuid,
                "description": description,
                "category": category,
                "confidence": confidence,
            }
        )
        if outcome.observations:
            runner = get_ingest_runner()
            if runner is not None:
                await runner.commit_outcome(outcome)
    except Exception:
        logger.debug(
            "identify_object: ingest runner side-channel skipped (runner unavailable)"
        )


async def _emit_trigger_event(event_type: str, data: dict) -> None:
    """Publish a trigger event on the DSG events channel."""
    try:
        from parrot.shared.constants import CH_DSG_EVENTS
        from parrot.shared.redis_client import get_redis
        r = await get_redis()
        payload = json.dumps({"type": event_type, **data})
        await r.publish(CH_DSG_EVENTS, payload)
    except Exception:
        logger.debug("Failed to emit trigger event %s", event_type)


# ─── reply formatting ─────────────────────────────────────────────────


def _merge_visual_hint(description: str, visual_hint: str) -> str:
    """Attach VLM details without hiding the user's original phrase."""
    base = description.strip()
    hint = visual_hint.strip()
    if not hint:
        return base
    if not base:
        return hint
    return f"{base}. Visual evidence detail: {hint}"


def _resolver_label(report: dict[str, Any], object_uuid: str) -> str:
    for candidate in report.get("candidate_objects") or []:
        if not isinstance(candidate, dict):
            continue
        if str(candidate.get("object_uuid") or "") == object_uuid:
            return str(candidate.get("label") or "")
    return ""


def _compact_text(text: str, limit: int) -> str:
    one_line = " ".join(str(text or "").split())
    if len(one_line) <= limit:
        return one_line
    return one_line[: max(0, limit - 1)].rstrip() + "..."


def _format_match_reply(
    *,
    stages: list[str],
    source: str,
    label: str,
    uuid: str,
    confidence: float,
) -> str:
    """Format a hit reply for the LLM. Stage info first, then the
    identification."""
    stage_block = "\n".join(stages)
    return (
        f"{stage_block}\n"
        f"identified: {label} (id={uuid}, source={source}, conf={confidence:.2f})\n"
        f"Speak naturally — this is YOUR recognition. Mention the object by "
        f"name like recognising a familiar face."
    )


def _evidence_payload(sample: "TimeAlignedSampleRef | None") -> dict[str, str]:
    """Small, secret-free event payload view of a visual evidence sample."""
    if sample is None:
        return {"evidence_id": "", "asset_uri": "", "asset_path": ""}
    return {
        "evidence_id": sample.evidence_id,
        "asset_uri": sample.asset_uri,
        "asset_path": sample.asset_path,
    }


def _format_unknown_reply(
    *,
    stages: list[str],
    description: str,
    snapshot_id: str,
    l0_candidates: list[tuple[str, str, float]],
    l1_results: list[dict[str, Any]],
    evidence_sample: "TimeAlignedSampleRef | None" = None,
) -> str:
    """Option α unknown reply — surfaces top candidates so the LLM can
    decide its next move (audit §9.4)."""
    stage_block = "\n".join(stages)
    pieces = [
        stage_block,
        f"unknown: '{description}' did not match anything in working memory or Graphiti.",
        f"snapshot_id: {snapshot_id or '(none)'}",
    ]
    if evidence_sample is not None:
        pieces.append(
            f"evidence_id: {evidence_sample.evidence_id} "
            f"({evidence_sample.kind}, asset={'yes' if evidence_sample.has_asset else 'no'})"
        )
    if l0_candidates:
        top_l0 = ", ".join(
            f"{lbl}({score:.2f})" for _u, lbl, score in l0_candidates[:_L0_TOP_K]
        )
        pieces.append(f"L0 near-misses: {top_l0}")
    if l1_results:
        top_l1 = ", ".join(
            (r.get("label", "") or "(unnamed)") for r in l1_results[:_L1_TOP_K]
        )
        pieces.append(f"L1 near-misses: {top_l1}")
    pieces.append(
        "You can: (a) say you don't know and ask the user; (b) call "
        "dispatch_task with task_type='research' to delegate to the maid "
        "(she will tell you when done); (c) describe what you see based on "
        "common sense; (d) call identify_object again with action='save_new' "
        "to remember it as a new object."
    )
    return "\n".join(pieces)
