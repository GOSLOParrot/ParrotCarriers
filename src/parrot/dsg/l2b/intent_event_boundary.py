"""IntentEventBoundaryHandler — L2-B cognitive boundary processor.

DSG-INTENT-EVENT-V1.

Triggers (IntentEventReason):
    TOOL_CALL_BOUNDARY    GOSLO calls a tool (manage_episode / set_mode /
                          dispatch_task / identify_object)
    NANOBOT_RESULT_RETURN A NanobotTask result flows back
    LONG_IDLE             ≥ configured idle threshold
    PLAN_PHASE_CHANGE     Plan transitions DRAFT/APPROVED/COMPLETE/...
    EXPLICIT              Explicit Brain tool / Trigger call

Desktop baseline behaviour:
    - Open new IntentEvent → tag active nodes (attention > threshold)
      with new ``event_id``
    - Close old IntentEvent → invoke decay strategy + fold strategy
    - Default: NoOpFoldStrategy + NoOpDecayStrategy (master § 3.5
      "测试期不衰减" rule)

P3 upgrade points (interface ready, implementation deferred):
    FoldStrategy.fold(event_id)            RustworkX subgraph fold / Cluster
    AttentionDecayStrategy.decay(event_id) TWF / Ebbinghaus / quantization

Phase 4 § 8 L9 守护: this module reads/writes ``SemanticNode.attention``
(runtime payload field) but does NOT touch
``parrot.dsg.attention.threshold`` (which stays at L9-locked numeric
constants and BB-write boundary).
"""

from __future__ import annotations

import logging
import time
import uuid as uuid_lib
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from parrot.dsg.l2b_graph import L2BGraph

logger = logging.getLogger(__name__)


# ─── Reason / state ───────────────────────────────────────────────


class IntentEventReason(str, Enum):
    TOOL_CALL_BOUNDARY = "tool_call_boundary"
    NANOBOT_RESULT_RETURN = "nanobot_result_return"
    LONG_IDLE = "long_idle"
    PLAN_PHASE_CHANGE = "plan_phase_change"
    EXPLICIT = "explicit"


@dataclass
class IntentEventState:
    event_id: str
    reason: IntentEventReason
    opened_at: float
    closed_at: float = 0.0
    member_node_uuids: list[str] = field(default_factory=list)
    triggering_actor: str = ""
    related_plan_id: str = ""
    related_episode_id: str = ""


# ─── Strategy protocols ───────────────────────────────────────────


@dataclass(frozen=True)
class FoldResult:
    folded_node_uuids: tuple[str, ...]
    folded_edges_count: int
    cluster_id: str = ""


class FoldStrategy(Protocol):
    def fold(self, event_id: str, graph: "L2BGraph") -> FoldResult: ...


class NoOpFoldStrategy:
    """Desktop baseline — no fold; just enumerate members for tracing.

    # TODO(P3-fold-bionic): SKELETON. Real bionic fold strategies (留
    #   接口已就位，实施 P3) options:
    #     - SubgraphFoldStrategy:  use ``rustworkx.subgraph(g, [uuids])``
    #       to extract a frozen sub-PyDiGraph; tag a Cluster node in
    #       the parent graph; route cross-event edges through the cluster.
    #     - VFppFoldStrategy:      use ``rustworkx.vf2_mapping`` with
    #       ``call_limit=2000`` to detect schema-equivalent frozen sub-
    #       graphs (same shape recurring across IntentEvents) and unify
    #       them — applies the "experience matching" pattern.
    #     - SpreadingFoldStrategy: keep nodes but reduce inter-event
    #       edge weights so future activation traversal stops at the
    #       boundary unless explicit cross_event_channel is opened.
    #   See dsg-rustworkx-master § 2.5 + § 3.4 for VF2++ + Cluster
    #   patterns; § 3.5 for hop hard-cap (4 hops) which folds must respect.
    """

    def fold(self, event_id: str, graph: "L2BGraph") -> FoldResult:
        members = [n.uuid for n in graph.all_nodes() if n.event_id == event_id]
        return FoldResult(
            folded_node_uuids=tuple(members),
            folded_edges_count=0,
        )


class AttentionDecayStrategy(Protocol):
    def decay(self, event_id: str, graph: "L2BGraph") -> int: ...


class NoOpDecayStrategy:
    """Test-period default — never decay (master § 3.5 ratified)."""

    def decay(self, event_id: str, graph: "L2BGraph") -> int:
        return 0


class SimpleDecayStrategy:
    """Multiplicative attention decay on members of a closed IntentEvent.

    For each member node n:
        n.attention = max(0.0, n.attention * decay_factor)
    Returns the affected node count.
    """

    def __init__(self, decay_factor: float = 0.7) -> None:
        if not 0.0 <= decay_factor <= 1.0:
            raise ValueError("decay_factor must be in [0, 1]")
        self._factor = decay_factor

    def decay(self, event_id: str, graph: "L2BGraph") -> int:
        affected = 0
        for n in graph.all_nodes():
            if n.event_id == event_id:
                n.attention = max(0.0, n.attention * self._factor)
                affected += 1
        return affected


# ─── Handler ──────────────────────────────────────────────────────


class IntentEventBoundaryHandler:
    """Single-process IntentEvent cognitive-boundary controller."""

    def __init__(
        self,
        fold_strategy: FoldStrategy | None = None,
        decay_strategy: AttentionDecayStrategy | None = None,
        attach_threshold: float = 0.4,
    ) -> None:
        self._fold = fold_strategy or NoOpFoldStrategy()
        self._decay = decay_strategy or NoOpDecayStrategy()
        self._attach_threshold = attach_threshold
        self._events: dict[str, IntentEventState] = {}
        self._current_event_id: str = ""

    # ─── Open / close ──────────────────────────────────────────

    def open(
        self,
        reason: IntentEventReason,
        triggering_actor: str = "",
        related_plan_id: str = "",
        related_episode_id: str = "",
        related_node_uuids: tuple[str, ...] = (),
    ) -> IntentEventState:
        """Open a new IntentEvent. Closes any active one first."""
        try:
            from parrot.dsg.l2b_graph import get_l2b_graph
            graph = get_l2b_graph()
        except Exception:
            graph = None  # type: ignore[assignment]

        # Close active first
        if self._current_event_id:
            self._close_internal(self._current_event_id, graph)

        new_id = self._generate_event_id()
        state = IntentEventState(
            event_id=new_id,
            reason=reason,
            opened_at=time.time(),
            triggering_actor=triggering_actor,
            related_plan_id=related_plan_id,
            related_episode_id=related_episode_id,
            member_node_uuids=list(related_node_uuids),
        )
        self._events[new_id] = state
        self._current_event_id = new_id

        # Tag currently-active nodes (attention > threshold) so they
        # belong to this IntentEvent until close.
        if graph is not None:
            for node in graph.all_nodes():
                if node.attention > self._attach_threshold and not node.event_id:
                    node.event_id = new_id
                    state.member_node_uuids.append(node.uuid)

        # Timeline marker via L1.5 Pool (best-effort)
        self._mark_timeline("intent_event_open", state)

        return state

    def close(self, event_id: str = "") -> IntentEventState | None:
        """Close the named (or current) IntentEvent."""
        target_id = event_id or self._current_event_id
        if not target_id:
            return None
        try:
            from parrot.dsg.l2b_graph import get_l2b_graph
            graph = get_l2b_graph()
        except Exception:
            graph = None  # type: ignore[assignment]
        return self._close_internal(target_id, graph)

    def _close_internal(
        self, event_id: str, graph: "L2BGraph | None"
    ) -> IntentEventState | None:
        state = self._events.get(event_id)
        if state is None or state.closed_at > 0:
            return state

        if graph is not None:
            members = [n.uuid for n in graph.all_nodes() if n.event_id == event_id]
            state.member_node_uuids = list(set(state.member_node_uuids + members))
            try:
                self._decay.decay(event_id, graph)
            except Exception:
                logger.exception("decay strategy failed for %s", event_id)
            try:
                self._fold.fold(event_id, graph)
            except Exception:
                logger.exception("fold strategy failed for %s", event_id)

        state.closed_at = time.time()
        if self._current_event_id == event_id:
            self._current_event_id = ""

        self._mark_timeline("intent_event_close", state)
        return state

    # ─── Lookups ───────────────────────────────────────────────

    def current_event_id(self) -> str:
        return self._current_event_id

    def get_event_state(self, event_id: str) -> IntentEventState | None:
        return self._events.get(event_id)

    def list_events(
        self, episode_id: str | None = None
    ) -> list[IntentEventState]:
        out = list(self._events.values())
        if episode_id is not None:
            out = [e for e in out if e.related_episode_id == episode_id]
        return out

    def cross_event_channel(
        self, src_event_id: str, dst_event_id: str
    ) -> list:
        """Return SemanticEdges that span src/dst event_id (baseline:
        full enumeration; P3 may filter by channel weight / age)."""
        try:
            from parrot.dsg.l2b_graph import get_l2b_graph
            graph = get_l2b_graph()
        except Exception:
            return []

        src_uuids = {n.uuid for n in graph.all_nodes() if n.event_id == src_event_id}
        dst_uuids = {n.uuid for n in graph.all_nodes() if n.event_id == dst_event_id}

        edges = []
        for u in src_uuids:
            for tgt_node, edge in graph.get_edges_from(u):
                if tgt_node.uuid in dst_uuids:
                    edges.append(edge)
        return edges

    # ─── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _generate_event_id() -> str:
        return f"ev_{int(time.time())}_{uuid_lib.uuid4().hex[:4]}"

    def _mark_timeline(self, kind_str: str, state: IntentEventState) -> None:
        try:
            from parrot.dsg.l1_5 import (
                TimelineMarkerKind,
                get_l1_5_pool,
            )
            mapping = {
                "intent_event_open": TimelineMarkerKind.INTENT_EVENT_OPEN,
                "intent_event_close": TimelineMarkerKind.INTENT_EVENT_CLOSE,
            }
            kind = mapping.get(kind_str, TimelineMarkerKind.INTENT_EVENT_OPEN)
            get_l1_5_pool().mark(
                kind,
                payload={
                    "event_id": state.event_id,
                    "reason": state.reason.value,
                    "actor": state.triggering_actor,
                    "related_plan_id": state.related_plan_id,
                    "related_episode_id": state.related_episode_id,
                },
                related_node_uuids=tuple(state.member_node_uuids),
            )
        except Exception:
            logger.debug("intent_event timeline mark skipped")


# ─── Singleton + test injection ───────────────────────────────────

_handler: IntentEventBoundaryHandler | None = None


def get_intent_event_handler() -> IntentEventBoundaryHandler:
    global _handler
    if _handler is None:
        _handler = IntentEventBoundaryHandler()
    return _handler


def set_intent_event_handler_for_test(
    handler: IntentEventBoundaryHandler | None,
) -> None:
    global _handler
    _handler = handler


__all__ = [
    "AttentionDecayStrategy",
    "FoldResult",
    "FoldStrategy",
    "IntentEventBoundaryHandler",
    "IntentEventReason",
    "IntentEventState",
    "NoOpDecayStrategy",
    "NoOpFoldStrategy",
    "SimpleDecayStrategy",
    "get_intent_event_handler",
    "set_intent_event_handler_for_test",
]
