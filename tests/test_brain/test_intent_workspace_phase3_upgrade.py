"""Phase 3 IntentWorkspace upgrade — disk recover, scope chain, pressure
callbacks, and role-based listing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from parrot.brain.intent_workspace import (
    IntentWorkspace,
    PayloadSource,
    PressureLevel,
    PressureReport,
    ScopedIntentWorkspace,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
)
from parrot.brain.intent_workspace_backend import DiskBackend, InMemoryBackend


def _req(
    *,
    kind: StagedRefKind = StagedRefKind.OTHER,
    payload: str | bytes = "x",
    payload_source: PayloadSource = PayloadSource.INLINE_TEXT,
    intent_event_id: str = "",
    related_plan_id: str = "",
    origin: str = "test",
    custom: dict | None = None,
) -> StagedRefRequest:
    return StagedRefRequest(
        kind=kind,
        payload_source=payload_source,
        payload_value=payload,
        metadata=StagedRefMetadata(
            origin=origin,
            kind=kind,
            payload_source=payload_source,
            related_intent_event_id=intent_event_id,
            related_plan_id=related_plan_id,
            custom_meta=custom or {},
        ),
    )


# ─── Role-based filters ──────────────────────────────────────────────


async def test_list_active_filters_by_plan_id() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(payload="p1", related_plan_id="plan_a"))
    await ws.stage(_req(payload="p2", related_plan_id="plan_b"))
    a_only = ws.list_active(plan_id="plan_a")
    assert len(a_only) == 1
    assert a_only[0].metadata.related_plan_id == "plan_a"


async def test_list_active_filters_by_role() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(payload="d1", custom={"role": "plan_draft"}))
    await ws.stage(_req(payload="d2", custom={"role": "plan_step"}))
    drafts = ws.list_by_role("plan_draft")
    assert len(drafts) == 1
    assert drafts[0].metadata.custom_meta.get("role") == "plan_draft"


async def test_list_active_filters_by_origin_prefix() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(payload="a", origin="trigger:goslo_curiosity"))
    await ws.stage(_req(payload="b", origin="tool:identify_object"))
    triggers = ws.list_active(origin_prefix="trigger:")
    assert len(triggers) == 1


# ─── Pressure callback ──────────────────────────────────────────────


async def test_pressure_callback_fires_on_level_transition() -> None:
    ws = IntentWorkspace(max_memory_bytes=64)  # tiny to force pressure
    received: list[PressureReport] = []

    def cb(report: PressureReport) -> None:
        received.append(report)

    ws.register_pressure_callback(cb)
    # First call: OK (no payload yet) — first transition None → OK still fires.
    rep0 = ws.memory_pressure()
    assert rep0.pressure_level == PressureLevel.OK
    assert len(received) == 1
    # Stage 100 bytes to trip CRITICAL on a 64-byte budget.
    await ws.stage(_req(payload="x" * 100))
    rep1 = ws.memory_pressure()
    assert rep1.pressure_level == PressureLevel.CRITICAL
    assert len(received) == 2  # OK -> CRITICAL transition
    # Same level second time: callback does NOT fire again
    ws.memory_pressure()
    assert len(received) == 2


async def test_pressure_candidate_skips_protected_kinds() -> None:
    ws = IntentWorkspace(max_memory_bytes=2048)
    h_plan = await ws.stage(_req(kind=StagedRefKind.PLAN, payload="plan_body"))
    h_other = await ws.stage(_req(kind=StagedRefKind.OTHER, payload="filler"))
    rep = ws.memory_pressure()
    assert h_plan.ref_id not in rep.candidate_evictions
    assert h_other.ref_id in rep.candidate_evictions


async def test_unregister_pressure_callback() -> None:
    ws = IntentWorkspace()
    fired: list[int] = []

    def cb(_r):  # noqa: ANN001
        fired.append(1)

    ws.register_pressure_callback(cb)
    assert ws.unregister_pressure_callback(cb)
    ws.memory_pressure()
    assert fired == []


# ─── Multi-agent scope chain ────────────────────────────────────────


async def test_scope_inherits_parent_refs_and_sees_own() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(payload="parent_doc", custom={"role": "parent"}))
    plan = ws.scope(owner_id="plan_001")
    await plan.stage(_req(payload="child_doc", custom={"role": "plan_step"}))

    parent_view = ws.list_active()
    assert len(parent_view) == 2  # parent sees both

    child_view = plan.list_active()
    # Default include_parent=True: child sees parent + own
    assert len(child_view) == 2
    own_only = plan.list_active(include_parent=False)
    assert len(own_only) == 1
    assert own_only[0].metadata.custom_meta.get("role") == "plan_step"


async def test_scope_evict_only_affects_own_refs() -> None:
    ws = IntentWorkspace()
    parent_h = await ws.stage(_req(payload="parent"))
    plan = ws.scope(owner_id="plan_evict")
    child_h = await plan.stage(_req(payload="child"))

    # Child cannot evict parent ref
    assert await plan.evict(parent_h.ref_id) is False
    assert ws.fetch(parent_h.ref_id) is not None

    # Child can evict own ref
    assert await plan.evict(child_h.ref_id) is True
    assert ws.fetch(child_h.ref_id) is None


async def test_scope_shutdown_evicts_owned() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(payload="parent_keep"))
    plan = ws.scope(owner_id="plan_shutdown")
    await plan.stage(_req(payload="child_a"))
    await plan.stage(_req(payload="child_b"))

    n = await plan.shutdown()
    assert n == 2
    # Parent ref untouched
    remaining = ws.list_active()
    assert len(remaining) == 1


async def test_scope_idempotency_isolated_per_owner() -> None:
    """Same payload staged by two scopes yields two distinct ref_ids."""
    ws = IntentWorkspace()
    a = ws.scope(owner_id="actor_a")
    b = ws.scope(owner_id="actor_b")
    h_a = await a.stage(_req(payload="dup"))
    h_b = await b.stage(_req(payload="dup"))
    assert h_a.ref_id != h_b.ref_id


def test_scope_requires_non_empty_owner_id() -> None:
    ws = IntentWorkspace()
    with pytest.raises(ValueError):
        ws.scope("")


# ─── Disk recovery ───────────────────────────────────────────────────


async def test_disk_recover_rebuilds_index_after_restart(tmp_path: Path) -> None:
    base = tmp_path / "ws"
    backend1 = DiskBackend(base_path=base)
    md = StagedRefMetadata(
        origin="recovery_test",
        kind=StagedRefKind.RICH_REPORT,
        payload_source=PayloadSource.INLINE_TEXT,
        related_plan_id="plan_recover",
    )
    await backend1.put("ref_x", "saved_body", md)
    md_bytes = StagedRefMetadata(
        origin="recovery_test",
        kind=StagedRefKind.PHOTO,
        payload_source=PayloadSource.INLINE_BYTES,
    )
    await backend1.put("ref_y", b"\x00\x01\x02", md_bytes)

    # New backend instance — simulates process restart
    backend2 = DiskBackend(base_path=base)
    assert backend2.list_ref_ids() == []  # fresh in-memory index
    recovered = await backend2.recover()
    ids = {ref_id for ref_id, _ in recovered}
    assert {"ref_x", "ref_y"} <= ids
    # Payload pointers should be valid Paths to the on-disk bodies.
    by_id = dict(recovered)
    assert isinstance(by_id["ref_x"].payload, Path)
    assert by_id["ref_x"].payload.exists()
    assert by_id["ref_x"].payload.read_text(encoding="utf-8") == "saved_body"


async def test_workspace_recover_from_disk_attaches_indexes(tmp_path: Path) -> None:
    base = tmp_path / "ws_workspace"
    backend1 = DiskBackend(base_path=base)
    md = StagedRefMetadata(
        origin="phase3",
        kind=StagedRefKind.PLAN,
        payload_source=PayloadSource.INLINE_TEXT,
        related_plan_id="plan_001",
        custom_meta={"role": "plan_draft"},
    )
    await backend1.put("ref_plan", "plan-json", md)
    await backend1.close()

    # Fresh workspace + fresh backend over the same directory
    ws = IntentWorkspace(backend=DiskBackend(base_path=base))
    n = await ws.recover_from_disk()
    assert n == 1
    refs = ws.list_active()
    assert len(refs) == 1
    assert refs[0].metadata.related_plan_id == "plan_001"
    assert refs[0].metadata.custom_meta.get("role") == "plan_draft"


async def test_in_memory_backend_recover_is_noop() -> None:
    ws = IntentWorkspace(backend=InMemoryBackend())
    n = await ws.recover_from_disk()
    assert n == 0
