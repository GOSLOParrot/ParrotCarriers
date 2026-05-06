"""L2-B attention extensions (decay + mechanism strategies).

Phase 4 § 8 L13 守护: This subpackage MUST NOT export an ``Attention``
class symbol at the top level (the L13 lock prevents misreads of
attention as a "fully landed L3 layer"). We export only the strategy
Protocols + concrete strategies + registries.

The legacy ``parrot.dsg.attention`` package (threshold.py + hint_writer.py)
remains untouched (Phase 4 § 8 L9 lock — numeric constants frozen).
This subpackage provides strategy-pattern hooks for **runtime decay**
and **associative activation**, used by ``IntentEventBoundaryHandler``
and Plan / IntentWorkspace consumers.
"""

from __future__ import annotations

from parrot.dsg.l2b.attention.decay import (
    AttentionDecayPolicy,
    NoOpAttentionDecayPolicy,
    SimpleAttentionDecayPolicy,
    get_attention_decay_policy,
    register_attention_decay_policy,
)
from parrot.dsg.l2b.attention.mechanism import (
    AttentionMechanism,
    BoundedBfsActivation,
    NoOpActivation,
    SpreadingActivationPlaceholder,
    get_attention_mechanism,
    register_attention_mechanism,
)

__all__ = [
    "AttentionDecayPolicy",
    "AttentionMechanism",
    "BoundedBfsActivation",
    "NoOpActivation",
    "NoOpAttentionDecayPolicy",
    "SimpleAttentionDecayPolicy",
    "SpreadingActivationPlaceholder",
    "get_attention_decay_policy",
    "get_attention_mechanism",
    "register_attention_decay_policy",
    "register_attention_mechanism",
]
