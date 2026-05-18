"""LineA Gemini Live turn-taking policy.

LineA uses Gemini Live's native audio turn detection.  For the phone demo we
keep that automatic end-of-turn detection, but disable barge-in so speaker
echo or accidental overlap cannot cut off the active answer.  The route-aware
Bluetooth lab can be revisited later; the default product behavior is
one-question-one-answer.
"""

from __future__ import annotations

import os
from typing import Any

_ENV_BARGE_IN = "PARROT_LINEA_BARGE_IN_ENABLED"
_TRUTHY = {"1", "true", "yes", "on", "enabled", "start_of_activity_interrupts"}


def linea_barge_in_enabled() -> bool:
    """Return whether LineA may interrupt Gemini's active speech.

    Default is disabled for the formal phone App.  Set
    ``PARROT_LINEA_BARGE_IN_ENABLED=1`` only for a deliberate low-latency lab
    run where overlapping speech is expected and output/input are isolated.
    """

    return os.getenv(_ENV_BARGE_IN, "").strip().lower() in _TRUTHY


def linea_turn_policy_status() -> dict[str, Any]:
    """Side-effect-free status payload for RoomSetting/HUD/Web read models."""

    barge_in = linea_barge_in_enabled()
    return {
        "env_key": _ENV_BARGE_IN,
        "barge_in_enabled": barge_in,
        "activity_handling": (
            "START_OF_ACTIVITY_INTERRUPTS" if barge_in else "NO_INTERRUPTION"
        ),
        "turn_detection": "native_model",
        "policy": "low_latency_overlap" if barge_in else "one_question_one_answer",
    }


def build_linea_realtime_input_config() -> Any | None:
    """Build the optional Google Realtime input config for LineA.

    Importing ``google.genai`` is intentionally deferred so read-only status
    routes can report the policy without requiring the realtime plugin stack to
    be importable.  ``None`` means "use provider defaults", which currently
    allow start-of-activity interruption.
    """

    if linea_barge_in_enabled():
        return None

    from google.genai import types as genai_types

    return genai_types.RealtimeInputConfig(
        activity_handling=genai_types.ActivityHandling.NO_INTERRUPTION,
    )
