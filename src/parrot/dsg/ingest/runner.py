"""ingest/runner — Observation → L2-B SemanticNode committer.

Sprint 2 T8. The Ingest **filters are pure** (`base.IngestFilter` contract);
this module is where their Observations actually become SemanticNodes in
the L2-B graph + obs_log entries.

Layered responsibilities (sprint2_plan §5.2):

    filter.process_*()         pure → emit Observation DTOs
         ↓
    runner.commit_outcome()    side-effects:
                                 - upsert into L2BGraph
                                 - apply authority override rules
                                 - log to parrot.obs_log
                                 - (Sprint 4) write back to Graphiti

Authority override (so tool/user confirmation wins over gemini_oral):
    When an incoming Observation shares a label/uuid with an existing node,
    we upgrade only if the new source has strictly higher authority. Same
    authority → merge facts, keep existing confirmation (avoid flapping).

Graphiti write-back is deferred (plan §8 Sprint 4 S4.B). The runner leaves
a `TODO(S4.B)` marker inline but does NOT call Graphiti here.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from parrot.brain.obs_log import log_obs_event
from parrot.dsg.ingest.base import IngestOutcome, Observation, ObservationSource
from parrot.dsg.l2b_graph import get_l2b_graph
from parrot.dsg.l2b_types import (
    ConfirmationStatus,
    Salience,
    SemanticNode,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Authority ordering (higher = wins). Mirrors the priority baked into
# `DetectionAuthority.priority()` but at the ObservationSource layer where
# CV tracks have already been folded into a single source tag.
_SOURCE_PRIORITY: dict[ObservationSource, int] = {
    ObservationSource.USER_TAG_OBSIDIAN: 100,
    ObservationSource.USER_EXPLICIT: 95,
    ObservationSource.IDENTIFY_OBJECT: 80,
    # GOSLO_AUTONOMOUS sits between user-asked (IDENTIFY_OBJECT=80)
    # and passive CV (CV_A10=60). Master § 3.3: GOSLO self-initiated
    # findings rank lower than user-prompted ones, higher than passive
    # CV detections so curiosity beats periodic re-identification.
    ObservationSource.GOSLO_AUTONOMOUS: 70,
    # Google Calendar is a user-owned external source. It should beat passive
    # CV, but it must not override explicit user/Obsidian authority.
    ObservationSource.GOOGLE_CALENDAR: 65,
    ObservationSource.CV_A10: 60,
    ObservationSource.CV_SENTINEL: 40,
    ObservationSource.GEMINI_ORAL: 30,
    ObservationSource.MOCK: 10,
}


class IngestRunner:
    """Commits Observations into L2-B working memory."""

    def __init__(self) -> None:
        self._graph = get_l2b_graph()
        # label → (last_seen_ts, source). Used for the 30s / 60s
        # "same label twice → promote TENTATIVE to CONFIRMED" rule
        # called out in `sprint2_plan §5.1`.
        self._label_cache: dict[str, tuple[float, ObservationSource]] = {}
        self._repeat_window_s = 30.0

    async def commit_outcome(self, outcome: IngestOutcome) -> int:
        """Commit every Observation carried by an IngestOutcome. Returns count.

        Before any commit we consult `mode_controller.is_enabled(filter_name)`
        so the active DsgMode gets a veto. Disabled filters still produce
        Observations (filters are pure — they don't know about modes), but
        the runner drops them here and logs a single obs entry explaining
        why. This keeps the enabled-set authoritative without coupling
        filter code to BB reads.
        """
        try:
            from parrot.dsg.mode_controller import get_mode_controller
            controller = get_mode_controller()
        except Exception:
            controller = None

        if controller is not None and not controller.is_enabled(outcome.filter_name):
            if outcome.observations:
                log_obs_event(
                    "ingest_mode_dropped",
                    layer=1,
                    payload={
                        "filter": outcome.filter_name,
                        "dropped": len(outcome.observations),
                        "current_mode": (
                            controller.current_mode().value
                            if controller.current_mode() else "unknown"
                        ),
                    },
                    actor=f"dsg.ingest.{outcome.filter_name}",
                )
            return 0

        committed = 0
        for obs in outcome.observations:
            if await self.commit_observation(obs):
                committed += 1

        if outcome.rejected:
            log_obs_event(
                "ingest_reject",
                layer=1,
                payload={
                    "filter": outcome.filter_name,
                    "rejected": outcome.rejected,
                    "reason": outcome.reason,
                },
                actor=f"dsg.ingest.{outcome.filter_name}",
            )
        return committed

    async def commit_observation(self, obs: Observation) -> bool:
        """Upsert one Observation. Returns True iff the graph changed."""
        try:
            existing = self._find_existing(obs)
            if existing is None:
                node = self._observation_to_node(obs)
                self._graph.upsert_node(node)
                changed = True
                action = "insert"
            else:
                changed = self._merge(existing, obs)
                action = "merge" if changed else "skip"

            # Repeat-seen promotion: same label within window AND from the
            # same source → bump confidence so Graphiti (Sprint 4) can later
            # promote to CONFIRMED. We update the cache regardless.
            now = time.time()
            prev = self._label_cache.get(obs.label.lower())
            self._label_cache[obs.label.lower()] = (now, obs.source)
            if (
                prev is not None
                and existing is not None
                and prev[1] == obs.source
                and (now - prev[0]) <= self._repeat_window_s
                and existing.confirmation == ConfirmationStatus.TENTATIVE
            ):
                existing.confirmation = ConfirmationStatus.CONFIRMED
                existing.evidence_score = min(1.0, existing.evidence_score + 0.25)
                changed = True
                action = "promote"

            log_obs_event(
                "ingest_commit",
                layer=1,
                payload={
                    "action": action,
                    "label": obs.label,
                    "source": obs.source.value,
                    "confidence": obs.confidence,
                    "confirmation": obs.confirmation.value,
                    "provenance_stream_id": obs.provenance_stream_id,
                },
                actor="dsg.ingest.runner",
            )

            # DSG-ARCHIVE-V1 (2026-05-06): NEVER write-back to Graphiti
            # here. CONFIRMED nodes flow through the three-phase delayed
            # archive pipeline:
            #   Phase 1 (this method): commit only to L2-B in-memory +
            #     L1.5 Pool metadata.
            #   Phase 2 (ConversationArchive.serialize): on conversation
            #     boundary, dump to disk.
            #   Phase 3 (nanobot idle, IdleArchiveTrigger): unified_filter
            #     + LLM → Graphiti.
            # See dsg_protocol_archive_v1_20260506.md.

            return changed
        except Exception:
            logger.exception("ingest runner: commit failed for %s", obs.label)
            return False

    def _find_existing(self, obs: Observation) -> SemanticNode | None:
        """Look up an existing node by stable source identity before label.

        Calendar events are deliberately excluded from the generic label
        fallback. A meeting title can easily match an object/person label; a
        Google event should only merge with another Google event carrying the
        same calendar/event identity.
        """
        if obs.source == ObservationSource.GOOGLE_CALENDAR:
            ref_key = _calendar_ref_key_from_obs(obs)
            if ref_key:
                for n in self._graph.all_nodes():
                    if _calendar_ref_key_from_node(n) == ref_key:
                        return n
            return None

        if obs.obsidian_uuid:
            for n in self._graph.all_nodes():
                if n.obsidian_uuid == obs.obsidian_uuid:
                    return n
        if obs.graphiti_uuid:
            for n in self._graph.all_nodes():
                if n.graphiti_uuid == obs.graphiti_uuid:
                    return n
        return self._graph.get_node_by_label(obs.label)

    def _merge(self, existing: SemanticNode, obs: Observation) -> bool:
        """Apply authority-respecting merge rules. Returns True iff mutated."""
        existing_priority = _SOURCE_PRIORITY.get(
            _source_for_node(existing), 0
        )
        new_priority = _SOURCE_PRIORITY.get(obs.source, 0)

        changed = False

        if obs.description and obs.description not in existing.known_facts:
            existing.known_facts.append(obs.description)
            changed = True

        # Stamp identifiers when the incoming has them and we don't.
        if obs.obsidian_uuid and not existing.obsidian_uuid:
            existing.obsidian_uuid = obs.obsidian_uuid
            changed = True
        if obs.graphiti_uuid and not existing.graphiti_uuid:
            existing.graphiti_uuid = obs.graphiti_uuid
            changed = True
        if obs.reference_image_path and not existing.reference_image_path:
            existing.reference_image_path = obs.reference_image_path
            changed = True
        if obs.last_sighting_path:
            existing.last_sighting_path = obs.last_sighting_path
            changed = True
        if obs.provenance_stream_id and not existing.provenance_stream_id:
            existing.provenance_stream_id = obs.provenance_stream_id
            changed = True

        if obs.source == ObservationSource.GOOGLE_CALENDAR:
            # Calendar refreshes should update the runtime event view in place
            # without creating a duplicate node. Source meta keeps the Google
            # identity/version tokens needed for later write-back.
            if obs.label and existing.label != obs.label:
                existing.label = obs.label
                changed = True
            if obs.description and existing.description != obs.description:
                existing.description = obs.description
                changed = True
            if existing.time_span != obs.time_span:
                existing.time_span = obs.time_span
                changed = True
            for key, value in obs.meta.items():
                if existing.source_meta.get(key) != value:
                    existing.source_meta[key] = value
                    changed = True

        existing.touch()

        # Confirmation upgrade: only let higher-authority sources change it.
        if new_priority >= existing_priority:
            if _confirmation_rank(obs.confirmation) > _confirmation_rank(existing.confirmation):
                existing.confirmation = obs.confirmation
                changed = True
            if obs.source in (
                ObservationSource.USER_EXPLICIT, ObservationSource.USER_TAG_OBSIDIAN,
            ):
                existing.salience = Salience.FOREGROUND
                changed = True

        return changed

    def _observation_to_node(self, obs: Observation) -> SemanticNode:
        """Build a SemanticNode from an Observation.

        Phase 4 → 5 transition (2026-05-04, ADR
        `adr_l1_5_source_dispatch_extension_space_20260504.md`):
        delegate to `SemanticNode.from_observation()` factory, which handles
        the source dispatch (Q1: Python only / Q2: meta+factory hybrid).
        We still apply the local `Salience` upgrade for user-sourced
        observations because that's a *runner-level* policy, not a
        per-source schema concern (the factory keeps the default ACTIVE).
        """
        node = SemanticNode.from_observation(obs)
        if obs.source in (
            ObservationSource.USER_EXPLICIT,
            ObservationSource.USER_TAG_OBSIDIAN,
        ):
            node.salience = Salience.FOREGROUND
        return node


def _source_for_node(node: SemanticNode) -> ObservationSource:
    """Map an existing node to its dominant source for authority comparison.

    Resolution order (Phase 4 → 5 transition, 2026-05-04):
      1. **Authoritative**: ``node.source`` (set by ``from_observation()``
         factory on Phase 4 W3+ ingestion paths). This is the right answer
         and skips heuristics.
      2. **Heuristic fallback**: identifier inference, kept for backward
         compat with pre-Phase-4 nodes (preloaded from Graphiti without
         going through IngestRunner; or test fixtures that construct
         SemanticNode bare). The mapping is conservative:
            obsidian_uuid    → USER_TAG_OBSIDIAN
            graphiti_uuid    → IDENTIFY_OBJECT
            otherwise         → GEMINI_ORAL
    """
    if node.source:
        try:
            return ObservationSource(node.source)
        except ValueError:
            # Node carries an unknown source string (forward-compat from a
            # newer pipeline) — fall through to the heuristic so the merge
            # logic still has a comparable priority value.
            pass
    if node.obsidian_uuid:
        return ObservationSource.USER_TAG_OBSIDIAN
    if node.graphiti_uuid:
        return ObservationSource.IDENTIFY_OBJECT
    return ObservationSource.GEMINI_ORAL


def _calendar_ref_key_from_obs(obs: Observation) -> tuple[str, str] | None:
    """Return the stable Google Calendar identity carried by an Observation."""
    calendar_id = str((obs.meta or {}).get("calendar_id", "primary") or "primary")
    event_id = str((obs.meta or {}).get("calendar_event_id", "") or "")
    if not event_id:
        return None
    return calendar_id, event_id


def _calendar_ref_key_from_node(node: SemanticNode) -> tuple[str, str] | None:
    """Return the stable Google Calendar identity carried by a SemanticNode."""
    if node.source != ObservationSource.GOOGLE_CALENDAR.value:
        return None
    source_meta = node.source_meta or {}
    event_id = str(source_meta.get("calendar_event_id", "") or "")
    if not event_id:
        return None
    calendar_id = str(source_meta.get("calendar_id", "primary") or "primary")
    return calendar_id, event_id


def _confirmation_rank(c: ConfirmationStatus) -> int:
    # GHOST < EXPECTED < TENTATIVE < UNCERTAIN < CONFIRMED
    return {
        ConfirmationStatus.GHOST: 0,
        ConfirmationStatus.EXPECTED: 1,
        ConfirmationStatus.TENTATIVE: 2,
        ConfirmationStatus.UNCERTAIN: 3,
        ConfirmationStatus.CONFIRMED: 4,
    }.get(c, 0)


_runner: IngestRunner | None = None


def get_ingest_runner() -> IngestRunner:
    global _runner
    if _runner is None:
        _runner = IngestRunner()
    return _runner


__all__ = ["IngestRunner", "get_ingest_runner"]
