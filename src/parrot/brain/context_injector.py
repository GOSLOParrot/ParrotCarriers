"""Context Injector (B12) — Gemini Live context push across 3 channels.

Sprint 1 T7 makes this module the single GOSLO→Gemini surface for
state-driven context:

    Channel  Method                              Used for
    ───────  ──────────────────────────────────  ───────────────────────────
    C2       session.update_instructions(text)   Persona / Scene switch
                                                 (existing memory + scene
                                                 block — unchanged)
    C3       session.update_chat_ctx + role=user Layer ③ light notice
             prefix "[状态] ..."                  (visual_state drift,
                                                 RPC rejections)
    C4       session.generate_reply(             Layer ③ heavy notice
               instructions=...)                 (BLOCKED, welcome-back
                                                 after PAUSED recovery)

## Why role=user for C3 (not system)

Gemini realtime silently drops `role=system` content passed via
`update_chat_ctx` (livekit/agents#4875, #3386). `update_instructions`
is a FULL REPLACE — too expensive for per-event notifications. We therefore
funnel layer ③ light events through `role=user` with a "[状态]" prefix so
Gemini treats them as conversational context it must acknowledge, not
silent instructions. See `sprint1_plan_20260422.md` §2 for the rationale.

## Blackboard subscription (1 Hz pull)

py-trees Blackboard does not ship a native on-change listener, so the
Injector polls a fixed set of 3-4 keys at 1 Hz, diffs against its last
snapshot, and fires `_on_bb_change` per key. Each event is rate-limited
to at most once per 3 s per key (R2 in Sprint 1 plan) and skipped while
Gemini is speaking (R3) — cognitive_state is available via BB once
agent.py wires it in Sprint 2. Until then, R3 stays best-effort.

Legacy `inject_memory` / `inject_scene` / `inject_notification` methods
keep their existing behaviour (C2 for memory/scene, C4 for notification).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from livekit.agents import AgentSession

from parrot.brain.soul import get_instructions, render_visual_constraints
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import BehaviorMode
from parrot.shared.vision_state import VisualState, VisualStateReason

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 60.0
_BB_POLL_INTERVAL_S = 1.0
_PER_KEY_MIN_GAP_S = 3.0
_STATUS_PREFIX = "[状态]"

# BB keys the Injector watches for change-driven context push.
_WATCHED_BB_KEYS: tuple[str, ...] = (
    "session/visual_state",
    "session/visual_reason",
    "tick/last_rpc_ack",
)


class ContextInjector:
    """Manages context injection into the Brain's Gemini session."""

    def __init__(self, session: AgentSession):
        self._session = session
        self._scene_context: str = ""
        self._memory_context: str = ""
        self._mode = BehaviorMode.BASE | BehaviorMode.COMPANION
        self._memory_task: asyncio.Task | None = None
        self._bb_task: asyncio.Task | None = None

        # BB observer — READ-only client (writer=None).
        self._bb = open_bb_client(name="context_injector", writer=None)
        self._last_seen: dict[str, Any] = {}
        self._last_sent_at: dict[str, float] = {}

    def set_mode(self, mode: BehaviorMode) -> None:
        """Update the active BehaviorMode. Called by mode_watcher on switch."""
        self._mode = mode

    # ───────────────────────── C2: full instructions rebuild ──────────────

    def _rebuild_instructions(self) -> str:
        base = get_instructions(self._mode)
        parts = [base]
        if self._memory_context:
            parts.append(
                f"\n[MEMORY CONTEXT]\n{self._memory_context}\n[/MEMORY CONTEXT]"
            )
        if self._scene_context:
            parts.append(
                f"\n[SCENE CONTEXT]\n{self._scene_context}\n[/SCENE CONTEXT]"
            )
        return "\n".join(parts)

    async def inject_memory(self, query: str = "recent important facts") -> None:
        """Pull relevant memories from Graphiti and inject into instructions."""
        try:
            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

            g = await get_graphiti()
            results = await g.search(
                query=query,
                group_ids=[PARTITIONS.GOSLO, PARTITIONS.USER],
                num_results=5,
            )

            if results:
                lines = []
                for r in results:
                    fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
                    lines.append(f"- {fact}")
                self._memory_context = "\n".join(lines)
            else:
                self._memory_context = ""

            self._session.update_instructions(self._rebuild_instructions())
            logger.debug(
                "context_injector: memory context updated (%d items)", len(results)
            )
        except Exception:
            logger.debug("context_injector: memory injection skipped")

    async def inject_scene(self, scene_summary: str) -> None:
        """Inject scene context (from DSG triggers or simulation)."""
        self._scene_context = scene_summary
        self._session.update_instructions(self._rebuild_instructions())
        logger.debug("context_injector: scene context updated")

    async def inject_notification(self, message: str) -> None:
        """Layer ③ heavy: make Gemini speak about it immediately (C4)."""
        await self._session.generate_reply(instructions=message)

    # ───────────────────────── C3: chat-ctx append (role=user) ────────────

    async def _push_status_user(self, body: str) -> None:
        """Append a `[状态] body` user-role message to Gemini's chat ctx (C3).

        Realtime-model-safe: role=user works on Gemini Live where role=system
        is silently dropped (livekit/agents#4875, #3386).
        """
        try:
            chat_ctx = self._session.chat_ctx.copy()
            chat_ctx.add_message(
                role="user", content=[f"{_STATUS_PREFIX} {body}"]
            )
            await self._session.update_chat_ctx(chat_ctx)
            logger.info("injector C3: %s %s", _STATUS_PREFIX, body)
        except Exception:
            logger.exception("injector C3: update_chat_ctx failed")

    async def _push_speech(self, body: str) -> None:
        """Layer ③ heavy (C4): ask Gemini to speak this now."""
        try:
            await self._session.generate_reply(instructions=body)
            logger.info("injector C4: %s", body)
        except Exception:
            logger.exception("injector C4: generate_reply failed")

    # ───────────────────────── BB subscription + dispatch ─────────────────

    def _read_bb(self, key: str) -> Any:
        try:
            return self._bb.get(key)
        except KeyError:
            return None

    def _classify_visual_state(
        self, old: Any, new: Any
    ) -> tuple[int, str | None, bool]:
        """Return (layer, message, heavy_flag).

        Message body is built from soul.render_visual_constraints() so the
        behavioural rules that Gemini must honour travel on the same channel
        as the signal itself — avoids the drift failure from audit §1.2.
        """
        if not isinstance(new, VisualState):
            return 1, None, False

        constraint = render_visual_constraints(new)
        reason = self._read_bb("session/visual_reason")
        reason_text = reason.value if isinstance(reason, VisualStateReason) else None

        if new == VisualState.BLOCKED:
            body = constraint or "视觉被遮挡"
            return 3, body, True
        if new == VisualState.PAUSED:
            heavy = not isinstance(old, VisualState) or old != VisualState.PAUSED
            body = constraint or "视觉暂停"
            if reason_text:
                body = f"{body} | 原因={reason_text}"
            return 3, body, heavy
        if new == VisualState.DEGRADED:
            body = constraint or "视觉降级"
            return 3, body, False
        if new == VisualState.ACTIVE:
            if isinstance(old, VisualState) and old in (
                VisualState.BLOCKED, VisualState.PAUSED
            ):
                return 3, "视觉恢复, 我又能看清了", True
            return 1, None, False
        return 1, None, False

    def _classify_rpc_ack(
        self, new: Any
    ) -> tuple[int, str | None, bool]:
        if not isinstance(new, dict) or new.get("ok", True):
            return 1, None, False
        rpc = new.get("rpc", "?")
        reason = new.get("reason", "?")
        detail = new.get("detail", "")
        text = f"RPC {rpc} 被 Unity 拒 ({reason})"
        if detail:
            text += f": {detail}"
        return 3, text, False

    def _classify_visual_reason(
        self, old: Any, new: Any
    ) -> tuple[int, str | None, bool]:
        # visual_reason is a feeder for visual_state — don't double-notify.
        # Reserved for future fine-grained UX; Sprint 1 keeps it at layer 1.
        return 1, None, False

    def _decide_layer(
        self, key: str, old: Any, new: Any
    ) -> tuple[int, str | None, bool]:
        """Return (layer_number, message_body_or_none, heavy_flag).

        layer=1 ⇒ no Gemini touch (subconscious only);
        layer=3 + heavy=False ⇒ C3 user-role append;
        layer=3 + heavy=True  ⇒ C4 generate_reply.
        Layer 2 (autonomous BB-only) is not emitted here in Sprint 1.
        """
        if key == "session/visual_state":
            return self._classify_visual_state(old, new)
        if key == "tick/last_rpc_ack":
            return self._classify_rpc_ack(new)
        if key == "session/visual_reason":
            return self._classify_visual_reason(old, new)
        return 1, None, False

    async def _dispatch(self, key: str, old: Any, new: Any) -> None:
        layer, body, heavy = self._decide_layer(key, old, new)
        if layer != 3 or not body:
            return

        now = time.time()
        if now - self._last_sent_at.get(key, 0.0) < _PER_KEY_MIN_GAP_S:
            logger.debug("injector: rate-limited %s (%.1fs ago)", key, now - self._last_sent_at.get(key, 0.0))
            return

        if heavy:
            await self._push_speech(body)
        else:
            await self._push_status_user(body)
        self._last_sent_at[key] = now

    async def _bb_poll_loop(self) -> None:
        """1 Hz: refuse-then-diff BB keys and dispatch layer-③ changes."""
        await asyncio.sleep(2.0)  # let session settle before first push

        # Pull-side: ensure VisualState is fresh before we diff.
        try:
            from parrot.brain.vision.state import recompute_visual_state
        except Exception:
            recompute_visual_state = None  # type: ignore[assignment]

        while True:
            try:
                if recompute_visual_state is not None:
                    try:
                        recompute_visual_state()
                    except Exception:
                        logger.debug("recompute_visual_state hiccup", exc_info=True)

                for key in _WATCHED_BB_KEYS:
                    new = self._read_bb(key)
                    old = self._last_seen.get(key, _SENTINEL)
                    if new != old:
                        # On the very first observation don't push — just
                        # record the baseline, to avoid "startup flood".
                        if old is _SENTINEL:
                            self._last_seen[key] = new
                            continue
                        try:
                            await self._dispatch(key, old, new)
                        finally:
                            self._last_seen[key] = new
            except Exception:
                logger.exception("injector: BB poll loop error")
            await asyncio.sleep(_BB_POLL_INTERVAL_S)

    # ───────────────────────── background tasks lifecycle ─────────────────

    async def _periodic_memory_poll(self) -> None:
        """Legacy: periodically refresh memory context (C2 rebuild)."""
        await asyncio.sleep(5.0)
        while True:
            try:
                await self.inject_memory()
            except Exception:
                logger.debug("context_injector: periodic memory poll error")
            await asyncio.sleep(_POLL_INTERVAL_S)

    def start_background(self) -> None:
        if self._memory_task is None or self._memory_task.done():
            self._memory_task = asyncio.create_task(self._periodic_memory_poll())
        if self._bb_task is None or self._bb_task.done():
            self._bb_task = asyncio.create_task(self._bb_poll_loop())

    async def stop(self) -> None:
        for task in (self._memory_task, self._bb_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


_SENTINEL = object()
_injector: ContextInjector | None = None


def attach_context_injector(session: AgentSession) -> ContextInjector:
    """Create and attach a ContextInjector to the Brain session."""
    global _injector
    _injector = ContextInjector(session)
    _injector.start_background()
    logger.info(
        "context_injector: attached (memory poll 60s, BB poll %.1fs, C3/C4 live)",
        _BB_POLL_INTERVAL_S,
    )
    return _injector


def get_context_injector() -> ContextInjector | None:
    """Get the active ContextInjector (if Brain is running)."""
    return _injector
