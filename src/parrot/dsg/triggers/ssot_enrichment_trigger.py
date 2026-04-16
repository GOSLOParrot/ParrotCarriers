"""SSOT Enrichment Trigger — boosts object confidence with Obsidian/Graphiti data.

Trigger mode: EVENT-DRIVEN (fires when new/uncertain objects appear in L2-B)

Flow:
  1. A new object enters L2-B (via identify_object tool or L1 detection)
  2. This trigger searches Graphiti scene + user partitions for matching info
  3. If Obsidian SSOT has data (synced to Graphiti), enriches the node with:
     - Known facts, typical location, category, tags
     - Boosts evidence_score → may upgrade EXPECTED → CONFIRMED
  4. If no SSOT match but object seems interesting → dispatch Nanobot research

This is the "credibility booster" — Obsidian SSOT provides ground truth that
raises our confidence in what we think we're seeing.
"""

from __future__ import annotations

import logging
from typing import Any

from parrot.dsg.l2b_types import ConfirmationStatus, Salience, SemanticNode
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerResult

logger = logging.getLogger(__name__)


class SSOTEnrichmentTrigger(BaseTrigger):
    """Enriches new/uncertain DSG nodes with SSOT data from Graphiti."""

    name = "ssot_enrichment"
    kinds = [TriggerKind.EVENT_DRIVEN]
    interval_seconds = 0

    def __init__(self, graph):
        super().__init__(graph)
        self._enriched_uuids: set[str] = set()

    async def on_startup(self) -> TriggerResult | None:
        return await self._enrich_all_uncertain()

    async def on_tick(self) -> TriggerResult | None:
        return await self._enrich_all_uncertain()

    async def on_event(self, event: dict[str, Any]) -> TriggerResult | None:
        """React to new object events."""
        event_type = event.get("type", "")

        if event_type in ("new_object", "object_discovered", "identify_result"):
            uuid = event.get("uuid", "")
            if uuid:
                return await self._enrich_single(uuid)

        if event_type == "scene_preloaded":
            return await self._enrich_all_uncertain()

        return None

    async def _enrich_single(self, uuid: str) -> TriggerResult | None:
        """Enrich a single node from SSOT."""
        if uuid in self._enriched_uuids:
            return None

        node = self._graph.get_node(uuid)
        if not node:
            return None

        enriched = await self._graph.enrich_from_obsidian(uuid)
        self._enriched_uuids.add(uuid)

        if enriched:
            return TriggerResult(
                trigger_name=self.name,
                summary=f"Enriched '{node.label}' from SSOT — confidence boosted",
                nodes_affected=[uuid],
            )

        if node.confirmation in (
            ConfirmationStatus.EXPECTED,
            ConfirmationStatus.TENTATIVE,
            ConfirmationStatus.UNCERTAIN,
        ):
            task_id = await self._dispatch_nanobot(
                task_type="research",
                params={
                    "query": f"What is '{node.label}'? Find details, typical use, category.",
                    "object_label": node.label,
                    "object_description": node.description or node.label,
                },
            )
            if task_id:
                return TriggerResult(
                    trigger_name=self.name,
                    summary=f"No SSOT data for '{node.label}' — dispatched research",
                    nodes_affected=[uuid],
                    dispatch_to_nanobot=True,
                    nanobot_task={"task_id": task_id, "object_uuid": uuid},
                )

        return None

    async def _enrich_all_uncertain(self) -> TriggerResult | None:
        """Batch-enrich all EXPECTED/UNCERTAIN nodes that haven't been processed."""
        uncertain = self._graph.filter_nodes(
            lambda n: (
                n.confirmation in (
                    ConfirmationStatus.EXPECTED,
                    ConfirmationStatus.TENTATIVE,
                    ConfirmationStatus.UNCERTAIN,
                )
                and n.uuid not in self._enriched_uuids
            )
        )

        if not uncertain:
            return None

        enriched_count = 0
        affected = []
        for node in uncertain:
            result = await self._enrich_single(node.uuid)
            if result:
                enriched_count += 1
                affected.extend(result.nodes_affected)

        if enriched_count:
            return TriggerResult(
                trigger_name=self.name,
                summary=f"Batch enriched {enriched_count}/{len(uncertain)} uncertain nodes",
                nodes_affected=affected,
            )
        return None
