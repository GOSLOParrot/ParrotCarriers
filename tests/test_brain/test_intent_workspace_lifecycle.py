"""BRAIN-INTENT-WS-V1 — IntentWorkspace lifecycle (stage / fetch / evict)."""

from __future__ import annotations

from pathlib import Path

import pytest

from parrot.brain.intent_workspace import (
    IntentWorkspace,
    PayloadSource,
    PressureLevel,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
)
from parrot.brain.intent_workspace_backend import (
    DiskBackend,
    InMemoryBackend,
)


def _req(
    kind: StagedRefKind = StagedRefKind.OTHER,
    payload_source: PayloadSource = PayloadSource.INLINE_TEXT,
    payload_value="hello",
    *,
    intent_event_id: str = "",
    auto_evict: bool = True,
    expires_at: float = 0.0,
    origin: str = "test",
) -> StagedRefRequest:
    return StagedRefRequest(
        kind=kind,
        payload_source=payload_source,
        payload_value=payload_value,
        metadata=StagedRefMetadata(
            origin=origin,
            kind=kind,
            payload_source=payload_source,
            related_intent_event_id=intent_event_id,
            auto_evict_on_intent_close=auto_evict,
            expires_at=expires_at,
        ),
    )


async def test_stage_returns_handle() -> None:
    ws = IntentWorkspace()
    h = await ws.stage(_req())
    assert h.ref_id
    assert h.kind == StagedRefKind.OTHER


async def test_stage_idempotent_on_same_payload_hash() -> None:
    ws = IntentWorkspace()
    h1 = await ws.stage(_req(payload_value="dup"))
    h2 = await ws.stage(_req(payload_value="dup"))
    assert h1.ref_id == h2.ref_id


async def test_fetch_returns_staged_ref() -> None:
    ws = IntentWorkspace()
    h = await ws.stage(_req(payload_value="payload"))
    ref = ws.fetch(h.ref_id)
    assert ref is not None
    assert ref.kind == StagedRefKind.OTHER


async def test_fetch_updates_last_accessed_at() -> None:
    import time
    ws = IntentWorkspace()
    h = await ws.stage(_req())
    first = ws.fetch(h.ref_id)
    assert first is not None
    time.sleep(0.001)
    second = ws.fetch(h.ref_id)
    assert second is not None
    assert second.metadata.last_accessed_at >= first.metadata.last_accessed_at


async def test_list_active_filters_by_intent_event() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(intent_event_id="ev_a", payload_value="a"))
    await ws.stage(_req(intent_event_id="ev_b", payload_value="b"))
    a_only = ws.list_active(intent_event_id="ev_a")
    assert len(a_only) == 1
    assert a_only[0].metadata.related_intent_event_id == "ev_a"


async def test_list_active_filters_by_kinds() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(kind=StagedRefKind.PHOTO, payload_value=b"img1"))
    await ws.stage(_req(kind=StagedRefKind.DOC, payload_value="doc"))
    photos = ws.list_active(kinds=frozenset({StagedRefKind.PHOTO}))
    assert len(photos) == 1
    assert photos[0].kind == StagedRefKind.PHOTO


async def test_evict_removes_from_index() -> None:
    ws = IntentWorkspace()
    h = await ws.stage(_req())
    assert await ws.evict(h.ref_id)
    assert ws.fetch(h.ref_id) is None
    assert await ws.evict(h.ref_id) is False


async def test_evict_intent_removes_all_intent_scoped() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req(intent_event_id="ev_x", payload_value="a"))
    await ws.stage(_req(intent_event_id="ev_x", payload_value="b"))
    await ws.stage(_req(intent_event_id="ev_y", payload_value="c"))
    n = await ws.evict_intent("ev_x")
    assert n == 2
    remaining = ws.list_active()
    assert len(remaining) == 1
    assert remaining[0].metadata.related_intent_event_id == "ev_y"


async def test_evict_intent_respects_auto_evict_flag() -> None:
    """Refs marked auto_evict_on_intent_close=False survive evict_intent."""
    ws = IntentWorkspace()
    await ws.stage(_req(intent_event_id="ev_pin", auto_evict=False))
    n = await ws.evict_intent("ev_pin")
    assert n == 0
    assert len(ws.list_active(intent_event_id="ev_pin")) == 1


async def test_evict_expired_scans_expires_at() -> None:
    import time
    ws = IntentWorkspace()
    past = time.time() - 1.0
    await ws.stage(_req(expires_at=past, payload_value="x"))
    await ws.stage(_req(payload_value="y"))
    n = await ws.evict_expired()
    assert n == 1


async def test_pressure_ok_below_threshold() -> None:
    ws = IntentWorkspace(max_memory_bytes=1024 * 1024)  # 1 MB
    await ws.stage(_req(payload_value="tiny"))
    rep = ws.memory_pressure()
    assert rep.pressure_level == PressureLevel.OK


async def test_in_memory_backend_put_get_delete() -> None:
    be = InMemoryBackend()
    md = StagedRefMetadata(
        origin="t", kind=StagedRefKind.OTHER,
        payload_source=PayloadSource.INLINE_TEXT,
    )
    await be.put("r1", "payload", md)
    assert "r1" in be.list_ref_ids()
    assert await be.delete("r1") is True
    assert "r1" not in be.list_ref_ids()


async def test_disk_backend_persists_to_path(tmp_path: Path) -> None:
    be = DiskBackend(base_path=tmp_path / "ws")
    md = StagedRefMetadata(
        origin="t", kind=StagedRefKind.RICH_REPORT,
        payload_source=PayloadSource.INLINE_TEXT,
    )
    await be.put("r2", "report-body", md)
    txt_path = tmp_path / "ws" / "r2.txt"
    assert txt_path.exists()
    assert txt_path.read_text(encoding="utf-8") == "report-body"


async def test_disk_backend_delete_removes_files(tmp_path: Path) -> None:
    be = DiskBackend(base_path=tmp_path / "ws")
    md = StagedRefMetadata(
        origin="t", kind=StagedRefKind.RICH_REPORT,
        payload_source=PayloadSource.INLINE_BYTES,
    )
    await be.put("r3", b"binary", md)
    bin_path = tmp_path / "ws" / "r3.bin"
    assert bin_path.exists()
    await be.delete("r3")
    assert not bin_path.exists()


async def test_close_clears_all() -> None:
    ws = IntentWorkspace()
    await ws.stage(_req())
    await ws.stage(_req(payload_value="other"))
    await ws.close()
    assert len(ws.list_active()) == 0
