"""Scene Context Trigger — searches Graphiti for similar past scenes/situations.

Trigger mode: STARTUP + EVENT-DRIVEN

When to fire:
  - On startup: "What was happening last time in this scene?"
  - When scene switches (new zone entered)
  - When multiple objects form a recognizable pattern (e.g., laptop + coffee + notes = "工作中")

Flow:
  1. Collect current L2-B object labels
  2. Query Graphiti goslo/scene partitions for past episodes involving similar objects
  3. If match found → create CO_OCCURRED edges, inject "memory recall" context
  4. Also query Graphiti for any notes/habits related to current time + scene

This is the "déjà vu" trigger — "this scene reminds me of last Tuesday when..."
"""

from __future__ import annotations

import logging
import time
from typing import Any

from parrot.dsg.l2b_types import EdgeKind, NodeKind, Salience, SemanticEdge, SemanticNode
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome

logger = logging.getLogger(__name__)


class SceneContextTrigger(BaseTrigger):
    """Searches for similar past scenes to provide contextual memory."""

    name = "scene_context"
    kinds = [TriggerKind.STARTUP, TriggerKind.EVENT_DRIVEN]
    interval_seconds = 0

    def __init__(self, graph):
        super().__init__(graph)
        self._last_scene_hash: str = ""

    async def on_startup(self) -> TriggerOutcome | None:
        return await self._search_scene_context()

    async def on_tick(self) -> TriggerOutcome | None:
        return None

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        event_type = event.get("type", "")

        if event_type in ("scene_switch", "zone_entered", "scene_preloaded"):
            return await self._search_scene_context()

        if event_type == "objects_stabilized":
            current_hash = self._compute_scene_hash()
            if current_hash != self._last_scene_hash:
                self._last_scene_hash = current_hash
                return await self._search_scene_context()

        return None

    async def _search_scene_context(self) -> TriggerOutcome | None:
        """Search Graphiti for past episodes with similar objects."""
        objects = self._graph.query_by_kind(NodeKind.OBJECT)
        if not objects:
            return None

        labels = [n.label for n in objects[:10]]
        if not labels:
            return None

        try:
            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

            g = await get_graphiti()

            scene_query = f"scene with objects: {', '.join(labels)}"
            results = await g.search(
                query=scene_query,
                group_ids=[PARTITIONS.GOSLO, PARTITIONS.SCENE],
                num_results=5,
            )

            if not results:
                return None

            memories = []
            for r in results:
                fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
                memories.append(fact)

            hour = time.localtime().tm_hour
            time_query = f"what usually happens around {hour}:00 in this scene"
            time_results = await g.search(
                query=time_query,
                group_ids=[PARTITIONS.GOSLO, PARTITIONS.USER],
                num_results=3,
            )
            for r in time_results:
                fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
                if fact not in memories:
                    memories.append(fact)

            if not memories:
                return None

            notification = "[Memory recall] This scene reminds me of:\n"
            for mem in memories[:5]:
                notification += f"  - {mem[:80]}\n"

            return TriggerOutcome(
                trigger_name=self.name,
                summary=f"Found {len(memories)} related memories for current scene",
                nodes_affected=[n.uuid for n in objects[:5]],
                notify_gemini=True,
                notification_text=notification,
            )

        except Exception:
            logger.debug("scene_context: Graphiti search failed")
            return None

    def _compute_scene_hash(self) -> str:
        """Simple hash of current object labels for change detection."""
        objects = self._graph.query_by_kind(NodeKind.OBJECT)
        labels = sorted(n.label.lower() for n in objects)
        return "|".join(labels)
