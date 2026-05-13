"""Web-only py-trees Blackboard activity read model.

This module exposes a bounded, summaries-only view over py-trees'
``Blackboard.activity_stream``. It is intentionally a Web Console diagnostic
surface, not a shared App DTO or a write path.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import py_trees


def build_blackboard_activity_snapshot(*, limit: int = 40) -> dict[str, Any]:
    """Return a bounded Blackboard activity snapshot for operator inspection."""
    bounded_limit = max(1, min(int(limit or 40), 120))
    stream = py_trees.blackboard.Blackboard.activity_stream
    if stream is None:
        py_trees.blackboard.Blackboard.enable_activity_stream()
        stream = py_trees.blackboard.Blackboard.activity_stream

    items = list(getattr(stream, "data", []) or [])[-bounded_limit:]
    rows = [_activity_row(item) for item in items]
    by_scope = Counter(row["scope"] for row in rows if row["scope"])
    by_client = Counter(row["client_name"] for row in rows if row["client_name"])
    by_type = Counter(row["activity_type"] for row in rows if row["activity_type"])
    return {
        "success": True,
        "action": "blackboard.activity",
        "data": {
            "stream_enabled": stream is not None,
            "limit": bounded_limit,
            "count": len(rows),
            "activities": rows,
            "counts_by_scope": dict(sorted(by_scope.items())),
            "counts_by_client": dict(sorted(by_client.items())),
            "counts_by_type": dict(sorted(by_type.items())),
        },
        "audit": {
            "read_only": True,
            "web_only": True,
            "source": "py_trees.blackboard.Blackboard.activity_stream",
            "values": "summaries_only",
        },
    }


def _activity_row(item: Any) -> dict[str, Any]:
    key = _clean_key(getattr(item, "key", ""))
    return {
        "key": key,
        "scope": key.split("/", 1)[0] if "/" in key else key,
        "activity_type": _activity_type(getattr(item, "activity_type", "")),
        "client_name": str(getattr(item, "client_name", "") or ""),
        "client_id": str(getattr(item, "client_id", "") or ""),
        "current_type": type(getattr(item, "current_value", None)).__name__,
        "current_summary": _summary(getattr(item, "current_value", None)),
        "previous_type": type(getattr(item, "previous_value", None)).__name__,
        "previous_summary": _summary(getattr(item, "previous_value", None)),
    }


def _activity_type(value: Any) -> str:
    name = getattr(value, "name", "")
    return str(name or value or "")


def _clean_key(value: Any) -> str:
    return str(value or "").lstrip("/")


def _summary(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, (str, int, float, bool)):
        return str(value)[:160]
    if isinstance(value, dict):
        return f"dict(len={len(value)})"
    if isinstance(value, (list, tuple, set)):
        return f"{type(value).__name__}(len={len(value)})"
    return type(value).__name__


__all__ = ["build_blackboard_activity_snapshot"]
