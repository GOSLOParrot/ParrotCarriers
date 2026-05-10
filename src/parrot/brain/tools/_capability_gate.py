"""Small capability gate helpers for model-aware Brain tools."""

from __future__ import annotations

import os

from parrot.brain.model_manifest_registry import get_model_manifest_registry
from parrot.shared.model_manifest import DEFAULT_MODEL_ID


def active_model_id() -> str:
    value = _bb_value("global/active_model_id", "")
    if isinstance(value, str) and value.strip():
        return value.strip()
    env_value = os.getenv("PARROT_ACTIVE_MODEL_ID", "").strip()
    return env_value or DEFAULT_MODEL_ID


def resolve_model_id(model_id: str = "") -> str:
    return str(model_id or "").strip() or active_model_id()


def supports_capability(capability_id: str, model_id: str = "") -> bool:
    selected = resolve_model_id(model_id)
    return get_model_manifest_registry().supports(selected, capability_id)


def unsupported_message(capability_id: str, model_id: str = "") -> str:
    selected = resolve_model_id(model_id)
    available = sorted(get_model_manifest_registry().capability_ids(selected))
    if not available:
        return (
            f"Model '{selected}' does not declare capability '{capability_id}', "
            "and no capabilities are registered."
        )
    return (
        f"Model '{selected}' does not declare capability '{capability_id}'. "
        f"Available: {', '.join(available)}."
    )


def _bb_value(key: str, default: object) -> object:
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="capability_gate.read", writer=None)
        value = bb.get(key)
        return default if value is None else value
    except Exception:
        return default


__all__ = [
    "active_model_id",
    "resolve_model_id",
    "supports_capability",
    "unsupported_message",
]
