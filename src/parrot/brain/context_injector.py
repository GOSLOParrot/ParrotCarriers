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

from parrot.brain.obs_log import log_obs_event
from parrot.brain.soul import get_instructions, render_visual_constraints
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import BehaviorMode
from parrot.shared.tiers import DsgMode, VideoTier
from parrot.shared.vision_state import VisualState, VisualStateReason

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 60.0
_BB_POLL_INTERVAL_S = 1.0
_PER_KEY_MIN_GAP_S = 3.0
_STATUS_PREFIX = "[状态]"

# BB keys the Injector watches for change-driven context push.
# Sprint 2 T5 adds `session/video_tier` + `session/dsg_mode` so Supervisor
# decisions surface to Gemini via C3 (and C2 for VIDEO_OFF crosses).
_WATCHED_BB_KEYS: tuple[str, ...] = (
    "session/visual_state",
    "session/visual_reason",
    "session/video_tier",
    "session/dsg_mode",
    "tick/last_rpc_ack",
)

# Per-tier / per-mode cue fragments. Kept compact — Gemini only needs the
# "my vision changed, adjust what you say" nudge, not a full explanation.
_TIER_C3_CUES: dict[VideoTier, str] = {
    VideoTier.VIDEO_OFF: "视频暂时关了, 我只能靠声音和记忆陪你",
    VideoTier.VIDEO_GEMINI_ONLY: "现在走省流量模式, 我能看你但不做深度识别",
    VideoTier.VIDEO_FULL: "视觉全开了, 看得更仔细",
    VideoTier.VIDEO_BURST: "进入相机爆发模式, 抓几帧高清画面",
}

_MODE_C3_CUES: dict[DsgMode, str] = {
    DsgMode.DSG_TEXT_ONLY: "我的视觉辅助全休了, 你说什么我记什么",
    DsgMode.DSG_GEMINI_VISION: "视觉辅助只剩我自己看, 不确定时说'像是'",
    DsgMode.DSG_FULL: "视觉辅助全开, 我可以认物体",
    DsgMode.DSG_SENTINEL_AUX: "备用视觉开着, 精度一般, 别做最终判断",
}


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

    async def _try_update_instructions(self, rebuilt: str, reason: str) -> None:
        updater = getattr(self._session, "update_instructions", None)
        if callable(updater):
            updater(rebuilt)
            logger.debug("context_injector: update_instructions (%s)", reason)
            return

        logger.warning(
            "context_injector: AgentSession.update_instructions unavailable; "
            "skipping C2 rebuild (%s)",
            reason,
        )

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

            await self._try_update_instructions(
                self._rebuild_instructions(),
                "memory",
            )
            logger.debug(
                "context_injector: memory context updated (%d items)", len(results)
            )
        except Exception:
            logger.debug("context_injector: memory injection skipped")

    async def inject_scene(self, scene_summary: str) -> None:
        """Inject scene context (from DSG triggers or simulation)."""
        self._scene_context = scene_summary
        await self._try_update_instructions(self._rebuild_instructions(), "scene")
        logger.debug("context_injector: scene context updated")

    async def inject_notification(self, message: str) -> None:
        """Layer ③ heavy: make Gemini speak about it immediately (C4)."""
        from parrot.brain.session_policy import should_generate_reply

        if not should_generate_reply("context_injector.notification"):
            logger.info("injector C4 skipped by session policy: %s", message[:120])
            return
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
        from parrot.brain.session_policy import should_generate_reply

        if not should_generate_reply("context_injector.C4"):
            logger.info("injector C4 skipped by session policy: %s", body[:120])
            return
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

    def _classify_video_tier(
        self, old: Any, new: Any
    ) -> tuple[int, str | None, bool]:
        """VideoTier change → C3 cue (downgrades) or C4 speak (upgrade to FULL).

        Sprint 2 policy (plan §2):
            - Downgrade / side-grade → layer 3 C3 (quiet body-awareness nudge)
            - Upgrade to VIDEO_FULL after real outage → layer 3 C4 heavy so
              GOSLO actually announces "we're back" on the next turn
            - Cross into VIDEO_OFF requires a C2 soul_constraints rebuild, but
              that belongs to the injector's `_rebuild_instructions` path and
              is plumbed separately via `inject_scene` / `inject_memory`. Here
              we just surface the change on C3 so the chat history shows it.
        """
        if not isinstance(new, VideoTier):
            return 1, None, False
        cue = _TIER_C3_CUES.get(new)
        if cue is None:
            return 1, None, False

        if (
            isinstance(old, VideoTier)
            and new == VideoTier.VIDEO_FULL
            and old != VideoTier.VIDEO_FULL
        ):
            return 3, cue, True
        return 3, cue, False

    def _classify_dsg_mode(
        self, old: Any, new: Any
    ) -> tuple[int, str | None, bool]:
        """DsgMode change → C3 cue. Never heavy — DSG mode is behind-the-scenes."""
        if not isinstance(new, DsgMode):
            return 1, None, False
        cue = _MODE_C3_CUES.get(new)
        if cue is None:
            return 1, None, False
        return 3, cue, False

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
        if key == "session/video_tier":
            return self._classify_video_tier(old, new)
        if key == "session/dsg_mode":
            return self._classify_dsg_mode(old, new)
        return 1, None, False

    async def _dispatch(self, key: str, old: Any, new: Any) -> None:
        layer, body, heavy = self._decide_layer(key, old, new)

        # Always audit-log the decision (Layer 1 included) so offline
        # reflection can tell "we saw it but stayed silent on purpose"
        # from "we never saw it" (Sprint 1 T9, ar_feature_vision §3.5).
        audit_payload: dict[str, Any] = {
            "key": key,
            "old": old,
            "new": new,
            "heavy": heavy,
        }

        if layer != 3 or not body:
            log_obs_event("bb_change", layer, {**audit_payload, "sent": False})
            return

        now = time.time()
        gap = now - self._last_sent_at.get(key, 0.0)
        if gap < _PER_KEY_MIN_GAP_S:
            logger.debug("injector: rate-limited %s (%.1fs ago)", key, gap)
            log_obs_event(
                "dispatch_skip_ratelimit", layer,
                {**audit_payload, "gap_s": round(gap, 3), "body": body},
            )
            return

        if heavy:
            await self._push_speech(body)
        else:
            await self._push_status_user(body)
        self._last_sent_at[key] = now
        log_obs_event(
            "bb_change", layer,
            {**audit_payload, "sent": True, "channel": "C4" if heavy else "C3", "body": body},
        )

        # C2 rebuild on VIDEO_OFF boundary (sprint2_plan §2, §4.3).
        #
        # When the tier crosses into or out of VIDEO_OFF Gemini needs its
        # System Instructions refreshed — not just a chat-ctx nudge — because
        # the SOUL_CONSTRAINTS constraint language for PAUSED state changes the
        # grammar of what GOSLO is allowed to say (e.g. "only use your ears").
        # We call update_instructions() here, after the C3/C4 notification has
        # been dispatched, so the instruction rebuild doesn't race the body push.
        #
        # Rate-limiting: use the same per-key gap already enforced above, so we
        # never call update_instructions() more than once per 3 s for this key.
        if key == "session/video_tier" and isinstance(new, VideoTier):
            old_is_off = (old == VideoTier.VIDEO_OFF)
            new_is_off = (new == VideoTier.VIDEO_OFF)
            if old_is_off or new_is_off:
                try:
                    rebuilt = self._rebuild_instructions()
                    await self._try_update_instructions(rebuilt, "VIDEO_OFF boundary")
                    logger.info(
                        "injector C2: update_instructions on VIDEO_OFF boundary "
                        "(%s → %s)",
                        old, new,
                    )
                    log_obs_event(
                        "bb_change", 2,
                        {**audit_payload, "sent": True, "channel": "C2",
                         "body": "update_instructions (VIDEO_OFF boundary)"},
                    )
                except Exception:
                    logger.exception("injector C2: update_instructions failed on VIDEO_OFF boundary")

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
