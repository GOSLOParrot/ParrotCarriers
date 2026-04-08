"""ModuleManifest — lightweight mounting declaration.

Per audit report §8: manifest answers "what does the runtime need to know
at mount time", NOT "what will this module ever do in the future".

Behavior contracts (RPC methods, Blackboard keys, task envelopes, Graphiti
partitions) will be defined separately as real consumer code emerges.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from parrot.shared.types import Layer, ModuleType


@dataclass
class ModuleManifest:
    # --- Identity ---
    module_id: str
    module_type: ModuleType

    # --- Layer participation ---
    layers: list[Layer] = field(default_factory=lambda: [Layer.L1, Layer.L2])
    livekit_identity: str | None = None  # only when L1 in layers

    # --- Hard runtime constraints ---
    requires_gpu: bool = False
    health_check_interval_s: int = 30

    @property
    def participates_l1(self) -> bool:
        return Layer.L1 in self.layers

    @property
    def participates_l2(self) -> bool:
        return Layer.L2 in self.layers

    @property
    def participates_l3(self) -> bool:
        return Layer.L3 in self.layers
