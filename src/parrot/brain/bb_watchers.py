"""Blackboard watcher registry — unified subscription point for ``event_driven`` keys.

Sprint 0 declared ``BlackboardKey.event_driven=True`` for ~10 keys but the
listener wiring landed scattered across modules (``mode_watcher``,
``vision.state``, ``preset_loader``). This module collects them into a
single registry so:

    * ``brain.agent`` can attach **all** watchers from one entry point.
    * Tests can reset / mock watchers without shotgunning fixtures across
      modules.
    * New menu / preset events flow through the same plumbing — no
      bespoke Pub/Sub channel per block.

Architecture (Voyager twin-path Injector strategy, ar_feature_vision §3.6):

    * **turn-start snapshot** — Context Injector calls
      :func:`snapshot_turn_start_keys` to materialise the keys it wants to
      see at the top of an LLM turn (active_persona / active_model /
      active_scene / active_workspace / active_mode / scene / visual_state /
      body_state).
    * **event-driven** — :func:`register_watcher` lets a callback fire when
      a specific BB key transitions. Used for persona swap → reload
      instructions; scene swap → switch L1.5 SceneRegistry; mode swap →
      regenerate Soul instructions.

Watchers are intentionally synchronous + lightweight. Heavy work (LLM
re-inference, Redis publish, file IO) must hop into ``asyncio.create_task``
inside the callback so the BB write path stays unblocked.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from parrot.shared.bb_schema import BB_KEYS, BlackboardKey

logger = logging.getLogger(__name__)


# ─── Public Voyager-style snapshot keys ──────────────────────────────


TURN_START_SNAPSHOT_KEYS: tuple[str, ...] = (
    "global/active_persona_id",
    "global/active_model_id",
    "global/active_scene_id",
    "global/active_workspace_id",
    "global/active_mode",
    "global/attention_thresholds",
    "global/user_profile",
    "session/scene",
    "session/app_capability_mode",
    "session/visual_state",
    "tick/body_state",
)
"""Keys the Context Injector reads at the start of each LLM turn.

cognitive_state is intentionally *excluded* — the LLM IS that state, sending
it would be noise (ar_feature_vision §3.6 matrix). last_rpc_ack is also
excluded from the snapshot path; it's only injected on failures via the
event-driven path below.
"""


EVENT_DRIVEN_FAILURE_KEYS: tuple[str, ...] = (
    "tick/last_rpc_ack",
    "tick/last_ecp_ack",
)
"""Keys whose value is *only* relevant when the embedded ack indicates a
failure. Watchers on these keys filter ``ok==False`` before firing.
"""


# ─── Watcher dataclass ──────────────────────────────────────────────


WatcherFn = Callable[[str, Any, Any], None]
"""``(bb_key, old_value, new_value) -> None`` synchronous callback."""


@dataclass(frozen=True)
class WatcherSpec:
    """Single registration record."""

    name: str
    bb_key: str
    callback: WatcherFn
    fire_on_unchanged: bool = False


# ─── Registry singleton ─────────────────────────────────────────────


class BbWatcherRegistry:
    """Process-wide key → callbacks index.

    Threadsafe (RLock) because mode_watcher Redis Pub/Sub fires from a
    separate asyncio task while preset_loader.apply runs on the main
    coroutine.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_key: dict[str, list[WatcherSpec]] = defaultdict(list)
        self._last_value: dict[str, Any] = {}

    def register(self, spec: WatcherSpec) -> None:
        with self._lock:
            self._by_key[spec.bb_key].append(spec)
            logger.debug(
                "bb_watchers: registered %s on %s (%d total)",
                spec.name, spec.bb_key, len(self._by_key[spec.bb_key]),
            )

    def unregister_by_name(self, name: str) -> int:
        n = 0
        with self._lock:
            for key, specs in list(self._by_key.items()):
                kept = [s for s in specs if s.name != name]
                n += len(specs) - len(kept)
                if kept:
                    self._by_key[key] = kept
                else:
                    self._by_key.pop(key, None)
        return n

    def fire(self, bb_key: str, new_value: Any) -> None:
        """Invoke every callback registered for ``bb_key``.

        ``old_value`` is read from the registry's last-seen cache. Callbacks
        that registered with ``fire_on_unchanged=False`` (default) are
        skipped when ``new_value == old_value``.
        """
        with self._lock:
            specs = list(self._by_key.get(bb_key, ()))
            old_value = self._last_value.get(bb_key)
            self._last_value[bb_key] = new_value

        for spec in specs:
            if not spec.fire_on_unchanged and old_value == new_value:
                continue
            try:
                spec.callback(bb_key, old_value, new_value)
            except Exception:
                logger.exception(
                    "bb_watchers: %s on %s callback failed", spec.name, bb_key,
                )

    def declared_event_driven_keys(self) -> tuple[BlackboardKey, ...]:
        """All BB_KEYS marked ``event_driven=True`` (registry inventory)."""
        return tuple(k for k in BB_KEYS if k.event_driven)

    def keys(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._by_key.keys())


_registry: BbWatcherRegistry | None = None


def get_watcher_registry() -> BbWatcherRegistry:
    global _registry
    if _registry is None:
        _registry = BbWatcherRegistry()
    return _registry


def set_watcher_registry_for_test(registry: BbWatcherRegistry | None) -> None:
    global _registry
    _registry = registry


# ─── Convenience registration helpers ────────────────────────────────


def register_watcher(
    name: str,
    bb_key: str,
    callback: WatcherFn,
    *,
    fire_on_unchanged: bool = False,
) -> None:
    """Sugar wrapper around :meth:`BbWatcherRegistry.register`."""
    get_watcher_registry().register(WatcherSpec(
        name=name,
        bb_key=bb_key,
        callback=callback,
        fire_on_unchanged=fire_on_unchanged,
    ))


def fire_watcher(bb_key: str, new_value: Any) -> None:
    """Sugar wrapper around :meth:`BbWatcherRegistry.fire`.

    Call this from any module that has just written ``bb_key`` if you want
    same-process subscribers to see the change immediately. Cross-process
    watchers (Redis Pub/Sub) are handled by their own modules.
    """
    get_watcher_registry().fire(bb_key, new_value)


def snapshot_turn_start_keys() -> dict[str, Any]:
    """Read the Voyager turn-start snapshot keys in one call.

    Returns a dict ``{bb_key: value_or_None}``. Missing / unreadable keys
    map to ``None`` so callers can tolerate partial state without try/except
    around every read.
    """
    out: dict[str, Any] = {}
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="bb_watchers.snapshot", writer=None)
        for key in TURN_START_SNAPSHOT_KEYS:
            try:
                out[key] = bb.get(key)
            except Exception:
                out[key] = None
    except Exception:
        for key in TURN_START_SNAPSHOT_KEYS:
            out[key] = None
    return out


# ─── Standard Brain watcher set ──────────────────────────────────────


def attach_standard_brain_watchers(
    *,
    on_persona_change: WatcherFn | None = None,
    on_mode_change: WatcherFn | None = None,
    on_scene_change: WatcherFn | None = None,
    on_model_change: WatcherFn | None = None,
    on_workspace_change: WatcherFn | None = None,
    extras: Iterable[WatcherSpec] = (),
) -> None:
    """One-call attachment for the menu watchers Brain.agent needs.

    Each callback is optional — leave None to skip. ``extras`` lets unit
    tests inject ad-hoc spies.
    """
    if on_persona_change is not None:
        register_watcher(
            "menu.persona", "global/active_persona_id", on_persona_change,
        )
    if on_mode_change is not None:
        register_watcher(
            "menu.mode", "global/active_mode", on_mode_change,
        )
    if on_scene_change is not None:
        register_watcher(
            "menu.scene", "global/active_scene_id", on_scene_change,
        )
    if on_model_change is not None:
        register_watcher(
            "menu.model", "global/active_model_id", on_model_change,
        )
    if on_workspace_change is not None:
        register_watcher(
            "menu.workspace", "global/active_workspace_id", on_workspace_change,
        )
    for spec in extras:
        get_watcher_registry().register(spec)


__all__ = [
    "BbWatcherRegistry",
    "EVENT_DRIVEN_FAILURE_KEYS",
    "TURN_START_SNAPSHOT_KEYS",
    "WatcherFn",
    "WatcherSpec",
    "attach_standard_brain_watchers",
    "fire_watcher",
    "get_watcher_registry",
    "register_watcher",
    "set_watcher_registry_for_test",
    "snapshot_turn_start_keys",
]
