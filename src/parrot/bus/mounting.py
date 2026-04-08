"""Staged mounting pipeline — unified lifecycle for all module types.

Per audit report §7: instead of branching into Path A / Path B,
use a single pipeline where each stage is conditionally executed
based on the module's layer participation.

Documents still use "Path A / Path B" as a mental model.
The code implements it as one pipeline with optional stages.

Lifecycle stages:
  1. preflight     — validate manifest, check preconditions
  2. attach_l2     — register on Redis, always runs
  3. attach_l1     — connect LiveKit Room (skipped for L2-only modules)
  4. start_heartbeat — begin periodic liveness proof
  5. publish_ready — announce module is online

Unmount reverses the order.
"""

from __future__ import annotations

import logging
from enum import Enum

from parrot.bus.heartbeat import HeartbeatSender
from parrot.bus.manifest import ModuleManifest
from parrot.bus.registry import deregister_module, register_module

logger = logging.getLogger(__name__)


class MountState(str, Enum):
    INIT = "init"
    PREFLIGHT = "preflight"
    L2_ATTACHED = "l2_attached"
    L1_ATTACHED = "l1_attached"
    HEARTBEAT_RUNNING = "heartbeat_running"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"


class ModuleMount:
    """Staged mounting pipeline for any module type."""

    def __init__(self, manifest: ModuleManifest):
        self.manifest = manifest
        self.state = MountState.INIT
        self._heartbeat = HeartbeatSender(
            manifest.module_id,
            interval_s=manifest.health_check_interval_s,
        )
        self._on_l1_attach = None  # callback set by L1 modules
        self._on_l1_detach = None

    def set_l1_hooks(self, attach, detach=None):
        """L1 modules provide their own LiveKit connection logic."""
        self._on_l1_attach = attach
        self._on_l1_detach = detach

    async def mount(self) -> None:
        """Run the full mounting pipeline."""
        mid = self.manifest.module_id

        # Stage 1: preflight
        self.state = MountState.PREFLIGHT
        if self.manifest.participates_l1 and not self.manifest.livekit_identity:
            raise ValueError(f"{mid}: L1 module must declare livekit_identity")
        layer_names = [layer.value for layer in self.manifest.layers]
        logger.info("[%s] preflight ok (layers=%s)", mid, layer_names)

        # Stage 2: attach L2 (always)
        await register_module(self.manifest)
        self.state = MountState.L2_ATTACHED
        logger.info("[%s] L2 attached (Redis registered)", mid)

        # Stage 3: attach L1 (conditional)
        if self.manifest.participates_l1:
            if self._on_l1_attach:
                await self._on_l1_attach()
            self.state = MountState.L1_ATTACHED
            logger.info("[%s] L1 attached (LiveKit)", mid)

        # Stage 4: start heartbeat
        await self._heartbeat.start()
        self.state = MountState.HEARTBEAT_RUNNING

        # Stage 5: ready
        self.state = MountState.READY
        logger.info("[%s] READY", mid)

    async def unmount(self) -> None:
        """Gracefully unmount, reversing mount order."""
        mid = self.manifest.module_id
        self.state = MountState.STOPPING

        await self._heartbeat.stop()

        if self.manifest.participates_l1 and self._on_l1_detach:
            await self._on_l1_detach()

        await deregister_module(mid)
        self.state = MountState.STOPPED
        logger.info("[%s] STOPPED", mid)
