"""Tests for bus module registry and mounting pipeline."""

import pytest

from parrot.bus.manifest import ModuleManifest
from parrot.bus.mounting import ModuleMount, MountState
from parrot.shared.types import Layer, ModuleType


@pytest.fixture
def brain_manifest() -> ModuleManifest:
    return ModuleManifest(
        module_id="brain-agent",
        module_type=ModuleType.CORE,
        layers=[Layer.L1, Layer.L2, Layer.L3],
        livekit_identity="brain",
    )


@pytest.fixture
def nanobot_manifest() -> ModuleManifest:
    return ModuleManifest(
        module_id="nanobot-worker",
        module_type=ModuleType.WORKER,
        layers=[Layer.L2],
    )


def test_manifest_l1_participation(brain_manifest, nanobot_manifest):
    assert brain_manifest.participates_l1 is True
    assert nanobot_manifest.participates_l1 is False


def test_manifest_l3_participation(brain_manifest, nanobot_manifest):
    assert brain_manifest.participates_l3 is True
    assert nanobot_manifest.participates_l3 is False


def test_manifest_slim():
    """After audit: manifest should only have identity + layers + hard constraints."""
    m = ModuleManifest(module_id="test", module_type=ModuleType.CORE)
    assert m.health_check_interval_s == 30
    assert m.requires_gpu is False
    assert m.livekit_identity is None
    assert not hasattr(m, "rpc_methods_provided")  # removed per audit §8.3
    assert not hasattr(m, "blackboard_keys_read")
    assert not hasattr(m, "external_channels")


def test_mount_preflight_l1_without_identity():
    """L1 module without livekit_identity should fail preflight."""
    m = ModuleManifest(
        module_id="bad",
        module_type=ModuleType.CORE,
        layers=[Layer.L1, Layer.L2],
        livekit_identity=None,
    )
    mount = ModuleMount(m)
    # Use asyncio.run() so the test isn't affected by other tests that
    # close the default event loop policy's loop (Phase 2 orchestrator
    # tests in tests/test_castle/ exercise asyncio.run() and leave the
    # main-thread loop in a "no current loop" state under
    # pytest-asyncio mode=auto on Python 3.11+).
    import asyncio

    with pytest.raises(ValueError, match="livekit_identity"):
        asyncio.run(mount.mount())


def test_mount_initial_state():
    m = ModuleManifest(module_id="test", module_type=ModuleType.WORKER, layers=[Layer.L2])
    mount = ModuleMount(m)
    assert mount.state == MountState.INIT
