"""P2.5: identify_object — on-demand object discovery and matching pipeline.

ARCHITECTURAL DECISION (D-P2.5-DISCOVER):
  We build this tool-based discovery path FIRST so that:
  1. Gemini Live can do on-demand "conscious" discovery via tools NOW
  2. A10's future full-vision pipeline will be "subconscious" — runs in
     background, never blocks Gemini's conversation or thinking
  3. Both paths feed the same Graphiti/DSG data model
  4. Building tool-first prevents us from designing everything around
     tool calls — A10 discovery will bypass tools entirely

Pipeline: discover → match known → (if new) save + dispatch background research
  → (later, on idle/session end) filter + annotate → persist to Graphiti

Sprint 2 Ingest wiring:
  `_save_new_object` calls `_ingest_via_runner` AFTER the legacy Graphiti write
  so that:
    a) the existing Graphiti episode add is preserved (long-term memory)
    b) the new IngestRunner authority pipeline also fires (audit log +
       IDENTIFY_OBJECT source priority for Sprint 4 Graphiti write-back)
  The two L2-B writes are idempotent — runner's upsert finds the node that
  `_upsert_to_l2b` just inserted and merges authority metadata onto it.

References:
  - Opus 17 §3: PhysicalObject Graphiti entity type, preload_object_semantics
  - Opus 19 §2: EXPECTED state, EvidenceAccumulator
  - Opus 19 §4.6: Gemini as fine-grained recognition engine
"""

from __future__ import annotations

import datetime
import json
import logging
import time
from typing import TYPE_CHECKING

from livekit.agents import RunContext, function_tool

if TYPE_CHECKING:
    from parrot.dsg.l2b_types import SemanticNode

logger = logging.getLogger(__name__)


@function_tool()
async def identify_object(
    context: RunContext,
    description: str,
    category: str = "",
    action: str = "match",
) -> str:
    """Identify, match, or save an object you see in the camera feed.

    Use this when:
    - The user asks "what is this?" or "do you recognize this?" (action=match)
    - You spot something new and want to save it for later (action=save_new)
    - You want to do a deep search for something you can't identify (action=deep_search)

    Args:
        description: Visual description (e.g., "blue ceramic mug", "silver laptop", "small brown bottle with white label").
        category: Optional category hint (e.g., "容器", "electronics", "furniture", "medicine").
        action: What to do — 'match' (quick Graphiti lookup), 'save_new' (remember as new object), 'deep_search' (dispatch background research).
    """
    if action == "match":
        return await _match_known(description, category)
    elif action == "save_new":
        return await _save_new_object(description, category)
    elif action == "deep_search":
        return await _deep_search(description, category)
    else:
        return await _match_known(description, category)


async def _ingest_via_runner(
    label: str,
    description: str,
    category: str,
    graphiti_uuid: str = "",
    confidence: float = 0.9,
) -> None:
    """Fire ToolResultFilter → IngestRunner as an audit side-channel.

    Called after the legacy Graphiti write in _save_new_object so that
    the Sprint 2 Ingest pipeline records an authoritative IDENTIFY_OBJECT
    Observation without replacing the existing L2-B upsert path.
    """
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
        logger.debug("identify_object: ingest runner side-channel skipped (runner unavailable)")


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


async def _upsert_to_l2b(
    uuid: str,
    description: str,
    category: str,
    *,
    from_graphiti: bool = False,
    graphiti_uuid: str = "",
) -> None:
    """Create or update a node in L2-B working memory."""
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
        logger.debug("L2-B upsert skipped (graph unavailable)")


async def _l2b_quick_match(description: str, category: str) -> "SemanticNode | None":
    """Sprint 3 Path 2: search L2-B working memory first.

    Uses substring label matching. Applies confidence >= 0.5 filter to reduce
    false positives from partial matches (e.g., "cat" hitting "black cat").
    Returns the best SemanticNode on hit, None on miss or graph unavailable.
    """
    try:
        from parrot.dsg.l2b_graph import get_l2b_graph
        from parrot.dsg.l2b_types import ConfirmationStatus, SemanticNode

        graph = get_l2b_graph()
        if graph is None or graph.node_count() == 0:
            return None

        node = graph.get_node_by_label(description)
        if node is None:
            return None

        # Confidence gate: N1 guard against over-eager substring recall.
        if node.evidence_score < 0.5:
            logger.debug(
                "L2-B hit for '%s' → node '%s' but evidence_score=%.2f < 0.5, skip",
                description, node.label, node.evidence_score,
            )
            return None

        # Only surface TENTATIVE and above (not GHOST nodes)
        if node.confirmation == ConfirmationStatus.GHOST:
            return None

        return node
    except Exception:
        logger.debug("L2-B quick match unavailable", exc_info=True)
        return None


async def _match_known(description: str, category: str) -> str:
    """Sprint 3 Path 2 + legacy Path 0: L2-B first, then Graphiti.

    Search order:
      1. L2-B working memory (fast, in-process) — sprint3_kickoff_prompt §T-P3
         On hit: update attention only, no Graphiti write, return "快速命中".
      2. Graphiti scene+user partitions (persistent) — original Sprint 2 path.
         On hit: upsert result into L2-B for future fast hits.
    """
    # Path 2: L2-B priority search
    l2b_node = await _l2b_quick_match(description, category)
    if l2b_node is not None:
        # Update attention without creating a Graphiti round-trip
        await _upsert_to_l2b(
            l2b_node.uuid, description, category,
            from_graphiti=False, graphiti_uuid=l2b_node.graphiti_uuid,
        )
        logger.info(
            "identify_object: L2-B fast hit → '%s' (uuid=%s, score=%.2f)",
            l2b_node.label, l2b_node.uuid, l2b_node.evidence_score,
        )
        return (
            f"L2-B 快速命中: '{l2b_node.label}' (可信度={l2b_node.evidence_score:.0%}, "
            f"状态={l2b_node.confirmation.value})。\n"
            f"这是我记忆中已见过的物体。描述: {l2b_node.description or '—'}。\n"
            "Confirm to the user naturally — this is YOUR recognition, "
            "like recognizing a familiar face. "
            "(Note: L2-B快速命中可能是部分匹配，请结合视觉确认。)"
        )

    # Path 0 (legacy): Graphiti full search
    try:
        import re

        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()

        query = f"object: {description}"
        if category:
            query += f" category: {category}"

        results = await g.search(
            query=query,
            group_ids=[PARTITIONS.SCENE, PARTITIONS.USER],
            num_results=5,
        )

        if not results:
            return (
                f"I don't recognize '{description}' from my known objects. "
                "This might be something new! "
                "You can call identify_object again with action='save_new' to remember it, "
                "or action='deep_search' to research it in the background."
            )

        _uuid_re = re.compile(r"\(uuid=([^)]+)\)")
        matches = []
        best_match = None
        for r in results:
            fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
            m = _uuid_re.search(fact)
            uuid_str = m.group(1) if m else ""
            clean_fact = _uuid_re.sub("", fact).strip()
            entry = f"- {clean_fact}"
            if uuid_str:
                entry += f" [id: {uuid_str}]"
            matches.append(entry)
            if best_match is None:
                best_match = {"uuid": uuid_str, "fact": clean_fact}

        if best_match and best_match["uuid"]:
            await _upsert_to_l2b(
                best_match["uuid"], description, category,
                from_graphiti=True, graphiti_uuid=best_match["uuid"],
            )

        result = f"Matches for '{description}':\n" + "\n".join(matches)

        if best_match and best_match["uuid"]:
            result += (
                f"\n\nBest match: {best_match['fact']} "
                f"(id: {best_match['uuid']}). "
                "Confirm to the user naturally — this is YOUR recognition, "
                "like recognizing a familiar face."
            )
        return result

    except Exception:
        logger.exception("identify_object._match_known failed")
        return "I can't search my object database right now — my memory is napping."


async def _save_new_object(description: str, category: str) -> str:
    """Save a newly discovered object to Graphiti + L2-B + emit trigger event."""
    try:
        from graphiti_core.nodes import EpisodeType

        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()

        import uuid as uuid_lib
        obj_uuid = str(uuid_lib.uuid4())[:12]

        text_parts = [f"New object discovered (uuid={obj_uuid}): {description}"]
        if category:
            text_parts.append(f"  category: {category}")
        text_parts.append(f"  discovered_at: {time.strftime('%Y-%m-%d %H:%M')}")
        text_parts.append("  status: newly_discovered, pending_enrichment")

        text = "\n".join(text_parts)

        await g.add_episode(
            name=f"gemini_discovery_{obj_uuid}",
            episode_body=text,
            source=EpisodeType.text,
            source_description=f"gemini_discovery:{obj_uuid}",
            reference_time=datetime.datetime.now(datetime.timezone.utc),
            group_id=PARTITIONS.SCENE,
        )

        await _upsert_to_l2b(obj_uuid, description, category)
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

        return (
            f"Saved new object '{description}' (id: {obj_uuid}). "
            "I'll remember it from now on. "
            "If you want me to research what this is, call identify_object "
            "with action='deep_search'."
        )

    except Exception:
        logger.exception("identify_object._save_new failed")
        return "I noticed something new but couldn't save it to my memory right now."


async def _deep_search(description: str, category: str) -> str:
    """Dispatch background research on an unrecognized object.

    Also saves a tentative L2-B node so the object is tracked immediately.
    Nanobot results come back via CH_TRIGGER_RESULTS → SSOTEnrichmentTrigger.
    """
    import uuid as uuid_lib
    obj_uuid = str(uuid_lib.uuid4())[:12]

    await _upsert_to_l2b(obj_uuid, description, category)

    try:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        params = {
            "query": f"Identify and research: {description}",
            "object_description": description,
            "object_uuid": obj_uuid,
            "category": category or "unknown",
            "result_channel": "identify_result",
            "instructions": (
                "Research this object. Find out: what it is exactly, "
                "its brand/model if applicable, typical use, and any "
                "interesting facts. Return structured info that can be "
                "saved to a knowledge graph."
            ),
        }

        task_id = await do_dispatch_task(
            task_type="research",
            params=params,
            priority="normal",
        )

        logger.info(
            "identify_object: deep search dispatched (task=%s) for: %s",
            task_id, description,
        )

        return (
            f"I've sent '{description}' to my research assistant (task: {task_id}). "
            "I'll let you know when I find out more! "
            f"I've saved it as a tentative object (id: {obj_uuid}) for now."
        )

    except Exception:
        logger.exception("identify_object._deep_search failed")
        return "I wanted to research this but my assistant is unavailable right now."
