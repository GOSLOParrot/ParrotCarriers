"""DSG ↔ Graphiti interface layer.

Provides the bridge functions that both the simulation script and
future real DSG will use to interact with Graphiti.
"""

from __future__ import annotations

import datetime
import json
import logging
import re
import time

from parrot.dsg.types import ObjectInfo, SceneTrigger, TriggerType
from parrot.shared.constants import CH_DSG_EVENTS, CH_DSG_SCENE_UPDATE
from parrot.shared.redis_client import get_redis

logger = logging.getLogger(__name__)


async def preload_object_semantics(object_id: str, label: str) -> dict | None:
    """Query Graphiti for known info about a detected object.

    Called when DSG sees an object — checks if we already know about it.
    Returns dict of known facts, or None if unknown.
    """
    try:
        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()
        results = await g.search(
            query=f"object: {label} (id: {object_id})",
            group_ids=[PARTITIONS.SCENE],
            num_results=3,
        )
        if results:
            facts = []
            for r in results:
                fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
                facts.append(fact)
            logger.debug("preload: found %d facts for %s", len(facts), label)
            return {"object_id": object_id, "label": label, "known_facts": facts}
        return None
    except Exception:
        logger.debug("preload: Graphiti unavailable for %s", label)
        return None


async def update_last_seen(
    object_id: str,
    label: str,
    position: tuple[float, float, float],
    zone: str = "",
    surface: str = "",
) -> None:
    """Update an object's last-seen position in Graphiti — bypasses LLM.

    This is a direct write for tracking purposes.
    """
    try:
        from graphiti_core.nodes import EpisodeType

        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()
        text = (
            f"Object '{label}' (id={object_id}) seen at position "
            f"({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f})"
        )
        if zone:
            text += f" in zone '{zone}'"
        if surface:
            text += f" on surface '{surface}'"

        await g.add_episode(
            name=f"dsg_seen_{object_id}",
            episode_body=text,
            source=EpisodeType.text,
            source_description="dsg_tracking",
            reference_time=datetime.datetime.now(datetime.timezone.utc),
            group_id=PARTITIONS.SCENE,
        )
        logger.debug("update_last_seen: %s at %s", label, position)
    except Exception:
        logger.debug("update_last_seen: Graphiti unavailable")


async def get_expected_objects(zone: str = "") -> list[ObjectInfo]:
    """Get list of objects expected to be in a zone (from Graphiti).

    Used by ExpectationChecker to compare against what's actually seen.
    """
    try:
        from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

        g = await get_graphiti()
        query = f"objects expected in zone '{zone}'" if zone else "known objects in scene"
        results = await g.search(
            query=query,
            group_ids=[PARTITIONS.SCENE],
            num_results=20,
        )
        objects = []
        _uuid_re = re.compile(r"\(uuid=([^)]+)\)")
        for r in results:
            fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
            m = _uuid_re.search(fact)
            obsidian_uuid = m.group(1) if m else ""
            label_text = _uuid_re.sub("", fact).strip()[:50]
            obj = ObjectInfo(
                object_id=obsidian_uuid or getattr(r, "uuid", ""),
                label=label_text or fact[:50],
                graphiti_uuid=getattr(r, "uuid", ""),
            )
            objects.append(obj)
        return objects
    except Exception:
        logger.debug("get_expected_objects: Graphiti unavailable")
        return []


async def emit_trigger(trigger: SceneTrigger) -> None:
    """Publish a scene trigger to Redis for Context Injector / Brain to pick up."""
    r = await get_redis()

    payload = json.dumps({
        "type": trigger.trigger_type.value,
        "object_id": trigger.object_info.object_id,
        "label": trigger.object_info.label,
        "position": list(trigger.object_info.position),
        "description": trigger.description,
        "timestamp": trigger.timestamp or time.time(),
    })

    await r.publish(CH_DSG_EVENTS, payload)
    logger.info(
        "emit_trigger: %s — %s (%s)",
        trigger.trigger_type.value,
        trigger.object_info.label,
        trigger.description,
    )


async def publish_scene_update(scene_summary: str) -> None:
    """Publish a scene summary to Redis for Context Injector."""
    r = await get_redis()
    await r.publish(CH_DSG_SCENE_UPDATE, scene_summary)
