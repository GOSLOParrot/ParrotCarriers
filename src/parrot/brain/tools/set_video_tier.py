"""set_video_tier — Gemini tool for user-initiated video tier switching.

Sprint 3 T-P1 originally used fire-and-forget Supervisor writes. Sprint 4
behavior governance upgrades this into a synchronous GOSLO Intent behavior:
the tool waits for Unity's `setVideoTier` applied/rejected result before it
returns, matching fly_to / animate and the identify_object audit's felt-
experience rule.

Manual override holds for PARROT_OVERRIDE_HOLD_SECONDS (default 300s / 5 min)
before Supervisor auto-manages again.

Routing: direct call to Supervisor (not through Router), with obs_log record
for Intent-layer audit. This is intentional per sprint3_kickoff_prompt.md N1:
"最简路径是 option 1（直调 set_manual_override）, 不增加 Router 复杂度."
"""

from __future__ import annotations

import json
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
    from parrot.brain.tools._state_context import attach_state_header
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
    result = await supervisor.request_manual_override(combo, hold_s=hold_s)

    log_obs_event(
        "intent_manual_tier",
        layer=2,
        payload={
            "requested_tier": tier_upper,
            "combo": [combo[0].value, combo[1].value],
            "hold_seconds": hold_s,
            "accepted": result.get("ok", False),
            "status": result.get("status"),
            "reason": result.get("reason"),
            "detail": result.get("detail"),
        },
        actor="brain.tools.set_video_tier",
    )

    if not result.get("ok", False):
        message = (
            f"我没能切换到{_TIER_LABELS.get(tier_upper, tier_upper)}。"
            f"原因: {result.get('reason', 'unknown')}。"
            f"{'细节: ' + str(result.get('detail')) if result.get('detail') else ''}"
        )
        # Sprint4 Phase 4 W3 selection-C (entry doc §8.1 L10): see fly_to.py.
        return attach_state_header(json.dumps(
            {
                "status": result.get("status", "rejected"),
                "tier": tier_upper,
                "ok": False,
                "reason": result.get("reason", "unknown"),
                "detail": result.get("detail", ""),
                "message": message,
            },
            ensure_ascii=False,
        ))

    logger.info(
        "set_video_tier: manual override %s → %s (hold=%.0fs)",
        result.get("status"), tier_upper, hold_s,
    )
    status = result.get("status", "applied")
    if status == "unchanged":
        message = f"已经在{_TIER_LABELS.get(tier_upper, tier_upper)}，不用重复切换。"
    else:
        message = (
            f"已切换到{_TIER_LABELS.get(tier_upper, tier_upper)}。"
            f"这个设置将保持约 {int(hold_s // 60)} 分钟，之后我会根据情况自动调整。"
        )
    # Sprint4 Phase 4 W3 selection-C (entry doc §8.1 L10): see fly_to.py.
    return attach_state_header(json.dumps(
        {
            "status": status,
            "tier": tier_upper,
            "ok": True,
            "reason": result.get("reason", "applied"),
            "hold_seconds": hold_s,
            "message": message,
        },
        ensure_ascii=False,
    ))


__all__ = ["set_video_tier"]
