"""L2-B subpackage — graph topology / Compartment views / attention extensions.

Naming hard rule (主设计稿 § 0.2):
    "Compartment" is L2-B-only. The L1.5 management plane uses "Bucket"
    (parrot.dsg.l1_5.buckets); never cross the terms.

Layout:
    parrot.dsg.l2b/
    ├── __init__.py                facade (re-exports)
    ├── views.py                   view_by_compartment / event / bucket / scene / kind
    ├── compartments.py            Compartment dataclass + cross-compartment edge
    ├── intent_event_boundary.py   IntentEventBoundaryHandler + decay / fold strategies
    └── attention/
        ├── decay.py               AttentionDecayPolicy strategy
        └── mechanism.py           AttentionMechanism strategy (4 candidates)

The legacy ``parrot.dsg.l2b_graph`` module remains the entry point for
L2BGraph (singleton) and stays as a facade for backward compatibility;
this subpackage adds **new** view / boundary / attention logic on top.
"""

from __future__ import annotations

from parrot.dsg.l2b.clustering import (
    Cluster,
    ClusterResult,
    ClusterStrategy,
    ConnectedComponentsClusterStrategy,
    NoOpClusterStrategy,
    get_cluster_strategy,
    register_cluster_strategy,
)
from parrot.dsg.l2b.compartments import (
    Compartment,
    CompartmentKind,
    is_cross_compartment_edge,
)
from parrot.dsg.l2b.intent_event_boundary import (
    AttentionDecayStrategy,
    FoldResult,
    FoldStrategy,
    IntentEventBoundaryHandler,
    IntentEventReason,
    IntentEventState,
    NoOpDecayStrategy,
    NoOpFoldStrategy,
    SimpleDecayStrategy,
    get_intent_event_handler,
    set_intent_event_handler_for_test,
)
from parrot.dsg.l2b.views import (
    view_by_bucket,
    view_by_event,
    view_by_kind,
    view_by_location,
    view_by_scene,
)

__all__ = [
    "AttentionDecayStrategy",
    "Cluster",
    "ClusterResult",
    "ClusterStrategy",
    "Compartment",
    "CompartmentKind",
    "ConnectedComponentsClusterStrategy",
    "FoldResult",
    "FoldStrategy",
    "IntentEventBoundaryHandler",
    "IntentEventReason",
    "IntentEventState",
    "NoOpClusterStrategy",
    "NoOpDecayStrategy",
    "NoOpFoldStrategy",
    "SimpleDecayStrategy",
    "get_cluster_strategy",
    "get_intent_event_handler",
    "is_cross_compartment_edge",
    "register_cluster_strategy",
    "set_intent_event_handler_for_test",
    "view_by_bucket",
    "view_by_event",
    "view_by_kind",
    "view_by_location",
    "view_by_scene",
]
