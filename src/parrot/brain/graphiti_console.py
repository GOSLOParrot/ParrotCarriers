"""Developer-console adapter for Graphiti memory-core management.

The Web console needs to inspect and test Graphiti without turning page loads
into memory writes. This adapter keeps reads, drafts, and explicit episode
writes separate. It degrades cleanly when the optional ``memory`` extra or the
graph database is not available.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any

from parrot.memory.graphiti_client import PARTITIONS

_GRAPHITI_MISSING_MESSAGE = "graphiti-core optional extra not installed"


@dataclass(frozen=True)
class GraphitiConsoleResult:
    """Serializable Graphiti operation result."""

    action: str
    success: bool
    available: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "success": self.success,
            "available": self.available,
            "message": self.message,
            "data": dict(self.data),
        }


def graphiti_status() -> GraphitiConsoleResult:
    """Return dependency/config status without opening a DB connection."""
    installed = _graphiti_core_installed()
    config_data: dict[str, Any] = {
        "installed": installed,
        "partitions": _partition_values(),
    }
    try:
        from parrot.shared.config import ParrotConfig

        cfg = ParrotConfig()
        config_data.update(
            {
                "falkordb": {
                    "host": cfg.falkordb.host,
                    "port": cfg.falkordb.port,
                    "database": cfg.falkordb.database,
                },
                "google_api_key_configured": bool(cfg.google_api_key),
                "gemini": {
                    "embedding_model": cfg.gemini.embedding_model,
                    "reranker_model": cfg.gemini.reranker_model,
                },
            }
        )
    except Exception as exc:
        config_data["config_error"] = f"{type(exc).__name__}: {exc}"

    message = "graphiti-core importable" if installed else _GRAPHITI_MISSING_MESSAGE
    return GraphitiConsoleResult(
        action="graphiti_status",
        success=True,
        available=installed,
        message=message,
        data=config_data,
    )


def draft_episode(
    *,
    name: str,
    body: str,
    partition: str = PARTITIONS.GOSLO,
    source_description: str = "app-web-console",
) -> GraphitiConsoleResult:
    """Build the exact episode draft the console would write."""
    selected_partition = _normalize_partition(partition)
    draft = {
        "name": name.strip() or "app_console_episode",
        "episode_body": body.strip(),
        "source": "text",
        "source_description": source_description.strip() or "app-web-console",
        "reference_time": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "group_id": selected_partition,
    }
    warnings: list[str] = []
    if not draft["episode_body"]:
        warnings.append("episode_body is empty; write endpoint will reject it")
    return GraphitiConsoleResult(
        action="draft_episode",
        success=True,
        available=_graphiti_core_installed(),
        message="draft only; no Graphiti write performed",
        data={"draft": draft, "warnings": warnings},
    )


async def search_graphiti(
    *,
    query: str,
    partition: str = PARTITIONS.GOSLO,
    limit: int = 5,
) -> GraphitiConsoleResult:
    """Search Graphiti with a scoped partition and graceful failure."""
    installed = _graphiti_core_installed()
    if not query.strip():
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=False,
            available=installed,
            message="query is required",
        )
    if not installed:
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=False,
            available=False,
            message=_GRAPHITI_MISSING_MESSAGE,
            data={"query": query, "partition": partition, "results": []},
        )
    try:
        from parrot.memory.graphiti_client import get_graphiti

        g = await get_graphiti()
        results = await g.search(
            query=query.strip(),
            group_ids=[_normalize_partition(partition)],
        )
        rows = [_serialize_search_hit(hit) for hit in list(results)[: max(1, min(limit, 20))]]
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=True,
            available=True,
            message=f"{len(rows)} result(s)",
            data={"query": query, "partition": partition, "results": rows},
        )
    except Exception as exc:
        return GraphitiConsoleResult(
            action="search_graphiti",
            success=False,
            available=_graphiti_core_installed(),
            message=f"{type(exc).__name__}: {exc}",
            data={"query": query, "partition": partition},
        )


async def add_episode(
    *,
    name: str,
    body: str,
    partition: str = PARTITIONS.GOSLO,
    source_description: str = "app-web-console",
    dry_run: bool = True,
) -> GraphitiConsoleResult:
    """Add a text episode only when dry_run is false and body is present."""
    installed = _graphiti_core_installed()
    draft = draft_episode(
        name=name,
        body=body,
        partition=partition,
        source_description=source_description,
    )
    episode = draft.data["draft"]
    if not episode["episode_body"]:
        return GraphitiConsoleResult(
            action="add_episode",
            success=False,
            available=installed,
            message="episode_body is required",
            data={"draft": episode},
        )
    if dry_run:
        return GraphitiConsoleResult(
            action="add_episode",
            success=True,
            available=installed,
            message="dry_run=true; no Graphiti write performed",
            data={"draft": episode},
        )
    if not installed:
        return GraphitiConsoleResult(
            action="add_episode",
            success=False,
            available=False,
            message=_GRAPHITI_MISSING_MESSAGE,
            data={"draft": episode},
        )

    try:
        from graphiti_core.nodes import EpisodeType

        from parrot.memory.graphiti_client import get_graphiti

        g = await get_graphiti()
        await g.add_episode(
            name=episode["name"],
            episode_body=episode["episode_body"],
            source=EpisodeType.text,
            source_description=episode["source_description"],
            reference_time=_dt.datetime.now(_dt.timezone.utc),
            group_id=episode["group_id"],
        )
        return GraphitiConsoleResult(
            action="add_episode",
            success=True,
            available=True,
            message="episode written",
            data={"episode": episode},
        )
    except Exception as exc:
        return GraphitiConsoleResult(
            action="add_episode",
            success=False,
            available=_graphiti_core_installed(),
            message=f"{type(exc).__name__}: {exc}",
            data={"draft": episode},
        )


def _partition_values() -> list[str]:
    return [PARTITIONS.GOSLO, PARTITIONS.MAID, PARTITIONS.SCENE, PARTITIONS.USER]


def _normalize_partition(raw: str) -> str:
    value = (raw or "").strip().lower()
    return value if value in _partition_values() else PARTITIONS.GOSLO


def _graphiti_core_installed() -> bool:
    try:
        import graphiti_core  # noqa: F401
    except ImportError:
        return False
    return True


def _serialize_search_hit(hit: Any) -> dict[str, Any]:
    text = (
        getattr(hit, "fact", None)
        or getattr(hit, "text", None)
        or getattr(hit, "summary", None)
        or str(hit)
    )
    return {
        "text": str(text)[:800],
        "score": getattr(hit, "score", None),
        "uuid": getattr(hit, "uuid", ""),
        "source_node_uuid": getattr(hit, "source_node_uuid", ""),
        "target_node_uuid": getattr(hit, "target_node_uuid", ""),
    }


__all__ = [
    "GraphitiConsoleResult",
    "add_episode",
    "draft_episode",
    "graphiti_status",
    "search_graphiti",
]
