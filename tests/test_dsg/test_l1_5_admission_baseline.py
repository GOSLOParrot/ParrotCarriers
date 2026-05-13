"""DSG-POOL-V1 § 3.2 — DesktopPolicy admission baseline.

Verifies the strategy-pattern admission decisions:
    1. confidence < theta_admit → REJECT(below_confidence)
    2. USER_TAG_OBSIDIAN routes to OBSIDIAN_SETTING_DAILY by default
    3. USER_TAG_OBSIDIAN with meta.profile=roleplay → OBSIDIAN_SETTING_ROLEPLAY
    4. GOSLO_AUTONOMOUS → AUTONOMOUS_CURIOSITY
    5. Other sources → MAIN
    6. USER-sourced observations get FOREGROUND salience override
"""

from __future__ import annotations

from parrot.dsg.ingest.base import Observation, ObservationSource
from parrot.dsg.l1_5.admission import (
    AdmissionContext,
    DesktopPolicy,
    get_admission_policy,
    register_admission_policy,
)
from parrot.dsg.l1_5.buckets import BucketKind
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind, Salience


def _obs(
    source: ObservationSource,
    *,
    label: str = "x",
    confidence: float = 0.5,
    meta: dict | None = None,
) -> Observation:
    return Observation(
        source=source,
        label=label,
        confidence=confidence,
        confirmation=ConfirmationStatus.TENTATIVE,
        kind=NodeKind.OBJECT,
        meta=dict(meta or {}),
    )


def test_below_confidence_rejected() -> None:
    p = DesktopPolicy(theta_admit=0.5)
    obs = _obs(ObservationSource.GEMINI_ORAL, confidence=0.2)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.admit is False
    assert decision.reject_reason == "below_confidence"


def test_above_confidence_admitted_main() -> None:
    p = DesktopPolicy(theta_admit=0.3)
    obs = _obs(ObservationSource.GEMINI_ORAL, confidence=0.7)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.admit is True
    assert decision.target_bucket == BucketKind.MAIN


def test_obsidian_daily_routing() -> None:
    p = DesktopPolicy()
    obs = _obs(
        ObservationSource.USER_TAG_OBSIDIAN,
        confidence=1.0,
        meta={"profile": "daily"},
    )
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.target_bucket == BucketKind.OBSIDIAN_SETTING_DAILY


def test_obsidian_roleplay_routing() -> None:
    p = DesktopPolicy()
    obs = _obs(
        ObservationSource.USER_TAG_OBSIDIAN,
        confidence=1.0,
        meta={"profile": "roleplay"},
    )
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.target_bucket == BucketKind.OBSIDIAN_SETTING_ROLEPLAY


def test_obsidian_default_profile_is_daily() -> None:
    """When meta.profile is missing, fall back to OBSIDIAN_SETTING_DAILY."""
    p = DesktopPolicy()
    obs = _obs(ObservationSource.USER_TAG_OBSIDIAN, confidence=1.0)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.target_bucket == BucketKind.OBSIDIAN_SETTING_DAILY


def test_goslo_autonomous_routing() -> None:
    p = DesktopPolicy()
    obs = _obs(ObservationSource.GOSLO_AUTONOMOUS, confidence=0.7)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.admit is True
    assert decision.target_bucket == BucketKind.AUTONOMOUS_CURIOSITY


def test_google_calendar_routing() -> None:
    p = DesktopPolicy()
    obs = _obs(ObservationSource.GOOGLE_CALENDAR, confidence=1.0)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.admit is True
    assert decision.target_bucket == BucketKind.GOOGLE_CALENDAR


def test_google_message_routing() -> None:
    p = DesktopPolicy()
    obs = _obs(ObservationSource.GOOGLE_MESSAGE, confidence=1.0)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.admit is True
    assert decision.target_bucket == BucketKind.GOOGLE_MESSAGE


def test_user_explicit_salience_promoted_to_foreground() -> None:
    p = DesktopPolicy()
    obs = _obs(ObservationSource.USER_EXPLICIT, confidence=0.7)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.salience_override == Salience.FOREGROUND


def test_user_tag_salience_promoted_to_foreground() -> None:
    p = DesktopPolicy()
    obs = _obs(ObservationSource.USER_TAG_OBSIDIAN, confidence=1.0)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.salience_override == Salience.FOREGROUND


def test_gemini_oral_salience_not_overridden() -> None:
    p = DesktopPolicy()
    obs = _obs(ObservationSource.GEMINI_ORAL, confidence=0.7)
    decision = p.evaluate(obs, AdmissionContext())
    assert decision.salience_override is None


def test_register_admission_policy_swaps_global() -> None:
    """Strategy registry: register_admission_policy swaps the singleton."""
    original = get_admission_policy()
    custom = DesktopPolicy(theta_admit=0.99)
    try:
        register_admission_policy(custom)
        assert get_admission_policy() is custom
    finally:
        register_admission_policy(original)
