"""DSG-POOL-V1 § 2.2 — Bucket lifecycle (register/freeze/clear/import)."""

from __future__ import annotations

import pytest

from parrot.dsg.l1_5.buckets import (
    BucketKind,
    BucketOp,
    BucketOpKind,
    BucketRegistry,
    BucketSpec,
)
from parrot.dsg.l1_5.pool import L15Pool, set_pool_for_test


@pytest.fixture
def pool():
    p = L15Pool()
    set_pool_for_test(p)
    yield p
    set_pool_for_test(None)


def test_default_buckets_present_after_init(pool: L15Pool) -> None:
    kinds = {h.spec.kind for h in pool.list_buckets()}
    assert BucketKind.MAIN in kinds
    assert BucketKind.OBSIDIAN_SETTING_DAILY in kinds
    assert BucketKind.OBSIDIAN_SETTING_ROLEPLAY in kinds
    assert BucketKind.GOOGLE_CALENDAR in kinds
    assert BucketKind.AUTONOMOUS_CURIOSITY in kinds


def test_register_bucket_idempotent(pool: L15Pool) -> None:
    spec = BucketSpec(kind=BucketKind.ROLEPLAY_TEMP, is_authority=True)
    h1 = pool.register_bucket(spec)
    h2 = pool.register_bucket(spec)
    assert h1 is h2  # identity == idempotent


@pytest.mark.asyncio
async def test_freeze_bucket_marks_handle(pool: L15Pool) -> None:
    h = pool.get_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    assert h is not None and not h.frozen
    await pool.freeze_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    assert h.frozen


@pytest.mark.asyncio
async def test_unfreeze_bucket_clears_flag(pool: L15Pool) -> None:
    await pool.freeze_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    h = pool.get_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    assert h is not None and h.frozen
    await pool.unfreeze_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    assert not h.frozen


@pytest.mark.asyncio
async def test_clear_bucket_evicts_node_uuids(pool: L15Pool) -> None:
    """Clear empties node_uuids set even if downstream graph is empty."""
    pool.buckets.add_node(BucketKind.GOOGLE_CALENDAR, "node_a")
    pool.buckets.add_node(BucketKind.GOOGLE_CALENDAR, "node_b")
    h = pool.get_bucket(BucketKind.GOOGLE_CALENDAR)
    assert h is not None and len(h.node_uuids) == 2
    await pool.clear_bucket(BucketKind.GOOGLE_CALENDAR)
    assert len(h.node_uuids) == 0


async def test_apply_bucket_op_register_via_dispatch(pool: L15Pool) -> None:
    """The bucket_op upload-channel hand-shakes to apply_bucket_op."""
    op = BucketOp(
        op=BucketOpKind.REGISTER,
        kind=BucketKind.ROLEPLAY_TEMP,
        payload={"spec": BucketSpec(
            kind=BucketKind.ROLEPLAY_TEMP, is_authority=True,
        )},
    )
    result = await pool.apply_bucket_op(op)
    assert result.success
    assert pool.get_bucket(BucketKind.ROLEPLAY_TEMP) is not None


def test_bucket_registry_idempotent_via_specdupes() -> None:
    reg = BucketRegistry()
    spec = BucketSpec(kind=BucketKind.MAIN)
    h1 = reg.register(spec)
    h2 = reg.register(spec)
    assert h1 is h2


def test_bucket_registry_find_node_owner() -> None:
    reg = BucketRegistry()
    reg.register(BucketSpec(kind=BucketKind.MAIN))
    reg.add_node(BucketKind.MAIN, "node_x")
    assert reg.find_bucket_of_node("node_x") == BucketKind.MAIN
    assert reg.find_bucket_of_node("missing_node") is None


@pytest.mark.asyncio
async def test_clear_then_unregister_removes_bucket(pool: L15Pool) -> None:
    pool.register_bucket(BucketSpec(kind=BucketKind.ROLEPLAY_TEMP))
    await pool.clear_bucket(BucketKind.ROLEPLAY_TEMP)
    op = BucketOp(op=BucketOpKind.UNREGISTER, kind=BucketKind.ROLEPLAY_TEMP)
    result = await pool.apply_bucket_op(op)
    assert result.success
    assert pool.get_bucket(BucketKind.ROLEPLAY_TEMP) is None
