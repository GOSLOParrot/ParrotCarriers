"""PlanBlackboard — py-trees Blackboard sub-namespace per Plan.

BRAIN-PLAN-V1 § 6.

Each Plan owns a side-blackboard at namespace ``plan/{plan_id}/`` so
PlanSteps can publish intermediate state without polluting the global
``scheduler/`` / ``transient/`` / ``session/`` namespaces.

Implementation note: in environments where py-trees blackboard isn't
available (e.g. unit tests without scheduler), a fallback in-memory
dict is used so PlanRegistry remains testable.
"""

from __future__ import annotations

from typing import Any


class PlanBlackboardClient:
    """Lightweight wrapper over py-trees Blackboard with fallback."""

    def __init__(self, plan_id: str) -> None:
        self._plan_id = plan_id
        self._namespace = f"plan/{plan_id}/"
        self._fallback: dict[str, Any] = {}
        self._client = None
        try:
            from parrot.scheduler.blackboard import open_bb_client
            self._client = open_bb_client(name=f"plan_{plan_id}", writer=None)
        except Exception:
            self._client = None

    def _key(self, key: str) -> str:
        return f"{self._namespace}{key}"

    def set(self, key: str, value: Any) -> None:
        full_key = self._key(key)
        if self._client is not None:
            try:
                self._client.set(full_key, value)
                return
            except Exception:
                pass
        self._fallback[full_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        full_key = self._key(key)
        if self._client is not None:
            try:
                return self._client.get(full_key)
            except Exception:
                pass
        return self._fallback.get(full_key, default)

    def delete(self, key: str) -> None:
        full_key = self._key(key)
        if self._client is not None:
            try:
                self._client.unset(full_key)
            except Exception:
                pass
        self._fallback.pop(full_key, None)

    def all_keys(self) -> list[str]:
        return list(self._fallback.keys())

    def cleanup(self) -> None:
        for k in list(self._fallback.keys()):
            self.delete(k.removeprefix(self._namespace) if k.startswith(self._namespace) else k)
        self._fallback.clear()


__all__ = ["PlanBlackboardClient"]
