"""DSG-SCENE-V1 — SceneType switch + bucket preservation."""

from __future__ import annotations

import pytest

from parrot.dsg.l1_5.buckets import BucketKind, BucketSpec
from parrot.dsg.l1_5.pool import L15Pool, set_pool_for_test
from parrot.dsg.l1_5.scene_snapshot import (
    DESKTOP_PROFILE,
    SceneProfile,
    SceneRegistry,
    SceneType,
)
from parrot.shared.tiers import DsgMode, VideoTier


@pytest.fixture
def pool():
    p = L15Pool()
    set_pool_for_test(p)
    yield p
    set_pool_for_test(None)


def test_default_current_scene_is_desktop(pool: L15Pool) -> None:
    assert pool.scenes.current_scene_type() == SceneType.DESKTOP
    profile = pool.current_scene()
    assert profile.scene_type == SceneType.DESKTOP


def test_desktop_profile_default_values() -> None:
    assert DESKTOP_PROFILE.scene_type == SceneType.DESKTOP
    assert DESKTOP_PROFILE.dsg_mode == DsgMode.DSG_GEMINI_VISION
    assert DESKTOP_PROFILE.video_tier_hint == VideoTier.VIDEO_GEMINI_ONLY
    assert DESKTOP_PROFILE.location_default == "desk"
    assert BucketKind.OBSIDIAN_SETTING_DAILY in DESKTOP_PROFILE.preserved_bucket_kinds
    assert BucketKind.GOOGLE_CALENDAR in DESKTOP_PROFILE.fresh_bucket_kinds


def test_register_alternate_scene_profile(pool: L15Pool) -> None:
    home = SceneProfile(
        scene_type=SceneType.HOME_INDOOR,
        dsg_mode=DsgMode.DSG_GEMINI_VISION,
        video_tier_hint=VideoTier.VIDEO_GEMINI_ONLY,
        preserved_bucket_kinds=frozenset({BucketKind.OBSIDIAN_SETTING_DAILY}),
        fresh_bucket_kinds=frozenset({BucketKind.GOOGLE_CALENDAR}),
        location_default="kitchen",
    )
    pool.scenes.register(home)
    assert pool.scenes.get(SceneType.HOME_INDOOR) is home


async def test_switch_scene_no_op_when_same(pool: L15Pool) -> None:
    out = await pool.switch_scene(SceneType.DESKTOP)
    assert out.success is True
    assert out.old_scene_type == out.new_scene_type == SceneType.DESKTOP


async def test_switch_scene_to_unregistered_fails_gracefully(pool: L15Pool) -> None:
    out = await pool.switch_scene(SceneType.OUTDOOR)
    assert out.success is False
    assert out.errors


async def test_switch_scene_freezes_authority_buckets(pool: L15Pool) -> None:
    home = SceneProfile(
        scene_type=SceneType.HOME_INDOOR,
        dsg_mode=DsgMode.DSG_GEMINI_VISION,
        video_tier_hint=VideoTier.VIDEO_GEMINI_ONLY,
        preserved_bucket_kinds=frozenset({BucketKind.OBSIDIAN_SETTING_DAILY}),
        fresh_bucket_kinds=frozenset({BucketKind.GOOGLE_CALENDAR}),
    )
    pool.scenes.register(home)
    # Pretend authority bucket has nodes
    pool.buckets.add_node(BucketKind.OBSIDIAN_SETTING_DAILY, "node_authority")
    out = await pool.switch_scene(SceneType.HOME_INDOOR)
    assert out.success is True
    assert out.new_scene_type == SceneType.HOME_INDOOR

    h = pool.get_bucket(BucketKind.OBSIDIAN_SETTING_DAILY)
    assert h is not None and h.frozen is True
    # authority node still present
    assert "node_authority" in h.node_uuids


async def test_switch_scene_clears_fresh_buckets(pool: L15Pool) -> None:
    home = SceneProfile(
        scene_type=SceneType.HOME_INDOOR,
        dsg_mode=DsgMode.DSG_GEMINI_VISION,
        video_tier_hint=VideoTier.VIDEO_GEMINI_ONLY,
        preserved_bucket_kinds=frozenset(),
        fresh_bucket_kinds=frozenset({BucketKind.GOOGLE_CALENDAR}),
    )
    pool.scenes.register(home)
    pool.buckets.add_node(BucketKind.GOOGLE_CALENDAR, "calendar_node_1")
    pool.buckets.add_node(BucketKind.GOOGLE_CALENDAR, "calendar_node_2")
    out = await pool.switch_scene(SceneType.HOME_INDOOR)
    assert out.success is True
    h = pool.get_bucket(BucketKind.GOOGLE_CALENDAR)
    assert h is not None
    assert len(h.node_uuids) == 0
