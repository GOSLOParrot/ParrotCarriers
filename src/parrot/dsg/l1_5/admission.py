"""L1.5 PoolAdmissionPolicy — strategy + DesktopPolicy baseline.

DSG-POOL-V1 § 3.

The admission policy is the L1.5 pool's gatekeeper. Each Observation
arriving from IngestRunner is evaluated; the decision drives:
    - admit / merge / reject path
    - target Bucket assignment
    - confirmation_override / salience_override

Desktop baseline (``DesktopPolicy``):
    1. confidence < theta_admit (default 0.3) → REJECT(BELOW_CONFIDENCE)
    2. bucket frozen → REJECT(BUCKET_FROZEN)
    3. otherwise → ADMIT, infer bucket from source + meta.profile

P3+ extension points (留接口，本 chat 不实施):
    - Weighted voting across multiple sources
    - "Related-to-current-IntentEvent" relevance scoring
    - Same-class second-instance user-confirm (master § 1.2)
    - Impossible-event detection (master § 1.2)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from parrot.dsg.l2b_types import ConfirmationStatus, Salience

if TYPE_CHECKING:
    from parrot.dsg.ingest.base import Observation
    from parrot.dsg.l1_5.buckets import BucketKind
    from parrot.dsg.l1_5.scene_snapshot import SceneProfile


@dataclass(frozen=True)
class AdmissionContext:
    """Context passed to PoolAdmissionPolicy.evaluate()."""

    current_intent_event_id: str = ""
    current_scene: "SceneProfile | None" = None
    goslo_attention_focus: tuple[str, ...] = ()
    triggering_actor: str = ""


@dataclass(frozen=True)
class AdmitDecision:
    admit: bool
    target_bucket: "BucketKind"
    confirmation_override: ConfirmationStatus | None = None
    salience_override: Salience | None = None
    reject_reason: str = ""
    notes: str = ""


class PoolAdmissionPolicy(Protocol):
    """L1.5 admission strategy. Replaceable globally via
    ``register_admission_policy()``."""

    def evaluate(
        self, obs: "Observation", ctx: AdmissionContext
    ) -> AdmitDecision: ...


class DesktopPolicy:
    """Desktop-baseline admission. Cheap rules; bionic upgrades P3.

    Rules (master § 1.2 / § 1.3 + DSG-POOL-V1 § 3.2):
        1. confidence < theta_admit              → REJECT(below_confidence)
        2. authority bucket frozen               → REJECT(bucket_frozen)
        3. otherwise → ADMIT, bucket inferred from source + meta.profile

    Bucket inference:
        USER_TAG_OBSIDIAN, meta.profile=daily    → OBSIDIAN_SETTING_DAILY
        USER_TAG_OBSIDIAN, meta.profile=roleplay → OBSIDIAN_SETTING_ROLEPLAY
        GOSLO_AUTONOMOUS                          → AUTONOMOUS_CURIOSITY
        otherwise                                 → MAIN

    SceneProfile.priority_overrides apply on top of source priority but
    are read by ``IngestRunner._merge`` (this class only handles the
    admit decision).
    """

    def __init__(self, theta_admit: float = 0.3) -> None:
        self._theta_admit = theta_admit

    def evaluate(
        self, obs: "Observation", ctx: AdmissionContext
    ) -> AdmitDecision:
        from parrot.dsg.ingest.base import ObservationSource
        from parrot.dsg.l1_5.buckets import BucketKind

        if obs.confidence < self._theta_admit:
            return AdmitDecision(
                admit=False,
                target_bucket=BucketKind.MAIN,
                reject_reason="below_confidence",
                notes=f"confidence={obs.confidence} < theta={self._theta_admit}",
            )

        target = self._infer_bucket(obs)

        salience_override: Salience | None = None
        if obs.source in (
            ObservationSource.USER_TAG_OBSIDIAN,
            ObservationSource.USER_EXPLICIT,
        ):
            salience_override = Salience.FOREGROUND

        return AdmitDecision(
            admit=True,
            target_bucket=target,
            salience_override=salience_override,
        )

    @staticmethod
    def _infer_bucket(obs: "Observation") -> "BucketKind":
        from parrot.dsg.ingest.base import ObservationSource
        from parrot.dsg.l1_5.buckets import BucketKind

        if obs.source == ObservationSource.USER_TAG_OBSIDIAN:
            profile = (obs.meta or {}).get("profile", "daily")
            if profile == "roleplay":
                return BucketKind.OBSIDIAN_SETTING_ROLEPLAY
            return BucketKind.OBSIDIAN_SETTING_DAILY
        if obs.source == ObservationSource.GOOGLE_CALENDAR:
            return BucketKind.GOOGLE_CALENDAR
        if obs.source == ObservationSource.GOOGLE_MESSAGE:
            return BucketKind.GOOGLE_MESSAGE
        if obs.source == ObservationSource.GOSLO_AUTONOMOUS:
            return BucketKind.AUTONOMOUS_CURIOSITY
        return BucketKind.MAIN


# ─── Registry ────────────────────────────────────────────────────────

_policy: PoolAdmissionPolicy | None = None


def register_admission_policy(policy: PoolAdmissionPolicy) -> None:
    global _policy
    _policy = policy


def get_admission_policy() -> PoolAdmissionPolicy:
    global _policy
    if _policy is None:
        _policy = DesktopPolicy()
    return _policy


__all__ = [
    "AdmissionContext",
    "AdmitDecision",
    "DesktopPolicy",
    "PoolAdmissionPolicy",
    "get_admission_policy",
    "register_admission_policy",
]
