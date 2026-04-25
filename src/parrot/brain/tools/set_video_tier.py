"""set_video_tier — Gemini tool for user-initiated video tier switching.

Sprint 3 T-P1. Implements decision D1: tool calls PerceptionSupervisor
.set_manual_override() rather than writing BB directly. This preserves the
single-writer contract (Supervisor is the sole writer of session/video_tier
and session/dsg_mode).

Manual override holds for PARROT_OVERRIDE_HOLD_SECONDS (default 300s / 5 min)
before Supervisor auto-manages again.

Routing: direct call to Supervisor (not through Router), with obs_log record
for Intent-layer audit. This is intentional per sprint3_kickoff_prompt.md N1:
"最简路径是 option 1（直调 set_manual_override）, 不增加 Router 复杂度."
"""

from __future__ import annotations

import logging

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool()
async def set_video_tier(
    context: RunContext,
    tier: str,
    hold_seconds: float = 0.0,
) -> str:
    """Switch GOSLO's video quality tier on demand.

    Call this when the user explicitly asks to change video quality
    (e.g., "全力开", "视频全开", "关掉摄像头", "省点流量").

    Args:
        tier: Target tier — one of:
            "VIDEO_FULL"         全力开 (1 Mbps/30fps, A10 全速)
            "VIDEO_GEMINI_ONLY"  省流模式 (300 kbps/15fps, 仅 Gemini)
            "VIDEO_OFF"          关闭摄像头 (完全关闭推流)
        hold_seconds: How long to hold this tier before auto-management
            resumes (seconds). 0 = use system default (PARROT_OVERRIDE_HOLD_SECONDS).
    """
    from parrot.brain.perception_supervisor import (
        MANUAL_OVERRIDE_HOLD_S,
        get_perception_supervisor,
    )
    from parrot.brain.obs_log import log_obs_event
    from parrot.shared.tiers import DsgMode, VideoTier

    _TIER_MAP: dict[str, tuple[VideoTier, DsgMode]] = {
        "VIDEO_FULL": (VideoTier.VIDEO_FULL, DsgMode.DSG_FULL),
        "VIDEO_GEMINI_ONLY": (VideoTier.VIDEO_GEMINI_ONLY, DsgMode.DSG_GEMINI_VISION),
        "VIDEO_OFF": (VideoTier.VIDEO_OFF, DsgMode.DSG_TEXT_ONLY),
    }
    _TIER_LABELS: dict[str, str] = {
        "VIDEO_FULL": "全力开（高清视频 + 全功能）",
        "VIDEO_GEMINI_ONLY": "省流模式（低码率视频）",
        "VIDEO_OFF": "摄像头已关闭",
    }

    tier_upper = tier.upper().replace(" ", "_")
    combo = _TIER_MAP.get(tier_upper)
    if combo is None:
        valid = ", ".join(_TIER_MAP)
        return (
            f"我不认识 '{tier}'。有效选项: {valid}。"
            "请用 VIDEO_FULL / VIDEO_GEMINI_ONLY / VIDEO_OFF 之一。"
        )

    supervisor = get_perception_supervisor()
    if supervisor is None:
        logger.warning("set_video_tier: Supervisor not attached yet")
        return "我现在还没准备好切换视频档位，稍等一下再试试？"

    hold_s = hold_seconds if hold_seconds > 0 else MANUAL_OVERRIDE_HOLD_S
    accepted = supervisor.set_manual_override(combo, hold_s=hold_s)

    log_obs_event(
        "intent_manual_tier",
        layer=2,
        payload={
            "requested_tier": tier_upper,
            "combo": [combo[0].value, combo[1].value],
            "hold_seconds": hold_s,
            "accepted": accepted,
        },
        actor="brain.tools.set_video_tier",
    )

    if not accepted:
        return (
            f"我试着切换到 {_TIER_LABELS.get(tier_upper, tier_upper)}，"
            "但这个组合不合法，保持原状。"
        )

    logger.info(
        "set_video_tier: manual override → %s (hold=%.0fs)",
        tier_upper, hold_s,
    )
    # The Supervisor writes Blackboard synchronously, then pushes Unity's
    # `setVideoTier` RPC asynchronously. Avoid claiming "switched" before the
    # phone has actually acknowledged the track rebuild/mute operation.
    return (
        f"好的，我已提交切换到{_TIER_LABELS.get(tier_upper, tier_upper)}的请求。"
        f"如果手机端确认失败，我会收到 RPC 状态并按视觉降级处理。"
        f"这个设置将保持约 {int(hold_s // 60)} 分钟，之后我会根据情况自动调整。"
    )


__all__ = ["set_video_tier"]
