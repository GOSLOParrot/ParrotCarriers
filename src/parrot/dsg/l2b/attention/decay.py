"""AttentionDecayPolicy — pluggable runtime attention decay.

Master § 3.5 ratified short-term default: **noop / no decay** during
the test period. Once real-machine smoke validates the decay rate, a
``SimpleAttentionDecayPolicy(half_life=...)`` can be registered.

Bionic upgrade path (P3+):
    - TWF (trust-weighted forgetting; see superlocalmemory § C)
    - Ebbinghaus exponential
    - Quantization (int8 attention payloads → variance grows)
    - Per-bucket decay rates
"""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from parrot.dsg.l2b_types import SemanticNode


class AttentionDecayPolicy(Protocol):
    """Pluggable per-tick attention decay strategy."""

    def decay(self, node: "SemanticNode", now: float | None = None) -> float:
        """Return the post-decay attention value (caller assigns it)."""
        ...


class NoOpAttentionDecayPolicy:
    """Test-period default — no decay (master § 3.5)."""

    def decay(self, node: "SemanticNode", now: float | None = None) -> float:
        return node.attention


class SimpleAttentionDecayPolicy:
    """Multiplicative decay: ``a' = a * (1 - factor*dt/tau)``.

    Where dt = now - node.last_attended and tau = time_constant_seconds.
    Capped at 0.0. P3 may swap for an Ebbinghaus / TWF curve.
    """

    def __init__(
        self,
        per_second_factor: float = 0.0005,
        time_constant_seconds: float = 60.0,
    ) -> None:
        self._factor = per_second_factor
        self._tau = max(1.0, time_constant_seconds)

    def decay(self, node: "SemanticNode", now: float | None = None) -> float:
        if now is None:
            now = time.time()
        dt = max(0.0, now - node.last_attended)
        decayed = node.attention * math.exp(-self._factor * dt / self._tau)
        return max(0.0, decayed)


# ─── Registry ────────────────────────────────────────────────────

_policy: AttentionDecayPolicy | None = None


def register_attention_decay_policy(policy: AttentionDecayPolicy) -> None:
    global _policy
    _policy = policy


def get_attention_decay_policy() -> AttentionDecayPolicy:
    global _policy
    if _policy is None:
        _policy = NoOpAttentionDecayPolicy()
    return _policy


__all__ = [
    "AttentionDecayPolicy",
    "NoOpAttentionDecayPolicy",
    "SimpleAttentionDecayPolicy",
    "get_attention_decay_policy",
    "register_attention_decay_policy",
]
