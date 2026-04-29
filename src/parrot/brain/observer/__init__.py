"""Sprint4 Phase 4 — `Observer` package ("记录" 职责，与 DSG L3 注意力分离).

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §3.7``
(observer / attention boundary) + §8.4 (code entry routing).

Boundary contract (re-stated here so it survives import-only readers)
---------------------------------------------------------------------
Observer = "记录" (recording). Inputs: EcpEvent stream from
:class:`parrot.brain.event_ingest.EcpEventIngest`, vision callbacks, RPC ack.
Outputs: BB transient writes + downstream EcpEvent emissions (when an Observer
needs to publish a brain-source event back, e.g. ``sighting.matched``).

**Forbidden**: weight calculation, threshold judgment, L2-B mutation, Graphiti
writes from Observer code. All four belong to ``parrot.dsg.attention.threshold``
(Phase 4 临时阈值器) or to existing dedicated paths (memory.archiver for
Graphiti, dsg.l2b_graph for L2-B).

Phase 4 starter modules (each one is a thin handler, not a heavyweight class):
    * :mod:`event_bus` — thin wrapper over EcpEventIngest that pre-wires the
      Phase 4 observer subscriptions in one place. Lets ``brain.agent`` call
      ``register_phase4_observers(ingest)`` instead of knowing each module.
    * :mod:`snapshot` — handles ``snapshot.captured`` from Unity, mirrors to
      BB ``transient/just_captured_photo``.
    * :mod:`sighting` — wires visual_match results to ``sighting.matched`` /
      ``sighting.unmatched`` outbound EcpEvents (brain source).
    * :mod:`photo` — handles ``photo.taken_preview`` + waits for matching
      ``photo.asset_uploaded`` to settle the asset_ref.
"""

from parrot.brain.observer.event_bus import register_phase4_observers


__all__ = ["register_phase4_observers"]
