"""L1.5 — DSG multi-source Node-exit management plane.

Phase 4 → 5 transition (DSG-POOL-V1, 2026-05-06).

Architecture (主设计稿 § 2.1, § 2.3):
    L1.5 is the **management plane** for the L2-B working memory graph.
    It does NOT own SemanticNode / SemanticEdge instances — those live in
    parrot.dsg.l2b_graph (single PyDiGraph). L1.5 owns metadata only:
        - BucketRegistry           (parrot.dsg.l1_5.buckets)
        - RefTable (lightweight)   (parrot.dsg.l1_5.ref_table)
        - Timeline (markers)       (parrot.dsg.l1_5.timeline)
        - SceneRegistry            (parrot.dsg.l1_5.scene_snapshot)
        - PoolAdmissionPolicy      (parrot.dsg.l1_5.admission)

Heavy payloads (full file bytes / GOSLO Intent-layer rich docs) live in
``parrot.brain.intent_workspace`` (BRAIN-INTENT-WS-V1), not here.

Naming hard rules (主设计稿 § 0.2):
    - "Bucket" is L1.5-only; never appears in L2-B / parrot.dsg.l2b/.
    - "IntentEvent" full name is required everywhere — "Event" alone forbidden.
    - "Scene" alone refers to SceneType; LocationTag is the position label.

Public API (re-exported here for ergonomic import):
    get_l1_5_pool() / set_pool_for_test() / L15Pool / AdmitOutcome / ...

Spec source:
    architecture/dsg/dsg_protocol_pool_v1_20260506.md
    architecture/dsg/dsg_protocol_scene_snapshot_v1_20260506.md
    architecture/dsg/dsg_l1_5_pool_and_lifecycle_design_20260506.md
"""

from __future__ import annotations

from parrot.dsg.l1_5.admission import (
    AdmissionContext,
    AdmitDecision,
    DesktopPolicy,
    PoolAdmissionPolicy,
    get_admission_policy,
    register_admission_policy,
)
from parrot.dsg.l1_5.buckets import (
    BucketHandle,
    BucketKind,
    BucketOp,
    BucketOpKind,
    BucketOpResult,
    BucketRegistry,
    BucketSpec,
)
from parrot.dsg.l1_5.pool import (
    AdmitOutcome,
    AdmitRejectReason,
    EvictReason,
    L15Pool,
    PoolCapacityPressure,
    PoolHealthReport,
    RejectedObservation,
    get_l1_5_pool,
    set_pool_for_test,
)
from parrot.dsg.l1_5.ref_table import (
    RefBinding,
    RefHealth,
    RefHealthStatus,
    RefKind,
    RefTable,
)
from parrot.dsg.l1_5.scene_snapshot import (
    DESKTOP_PROFILE,
    SceneProfile,
    SceneRegistry,
    SceneSwitchOutcome,
    SceneType,
)
from parrot.dsg.l1_5.timeline import (
    Timeline,
    TimelineMarker,
    TimelineMarkerKind,
)

__all__ = [
    # admission
    "AdmissionContext",
    "AdmitDecision",
    "DesktopPolicy",
    "PoolAdmissionPolicy",
    "get_admission_policy",
    "register_admission_policy",
    # buckets
    "BucketHandle",
    "BucketKind",
    "BucketOp",
    "BucketOpKind",
    "BucketOpResult",
    "BucketRegistry",
    "BucketSpec",
    # pool
    "AdmitOutcome",
    "AdmitRejectReason",
    "EvictReason",
    "L15Pool",
    "PoolCapacityPressure",
    "PoolHealthReport",
    "RejectedObservation",
    "get_l1_5_pool",
    "set_pool_for_test",
    # ref_table
    "RefBinding",
    "RefHealth",
    "RefHealthStatus",
    "RefKind",
    "RefTable",
    # scene
    "DESKTOP_PROFILE",
    "SceneProfile",
    "SceneRegistry",
    "SceneSwitchOutcome",
    "SceneType",
    # timeline
    "Timeline",
    "TimelineMarker",
    "TimelineMarkerKind",
]
