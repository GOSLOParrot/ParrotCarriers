"""Graphiti client singleton — FalkorDB backend + group_id partitioning.

Usage:
    from parrot.memory.graphiti_client import get_graphiti, PARTITIONS

    g = await get_graphiti()
    await g.add_episode(text="...", group_id=PARTITIONS.GOSLO, ...)
    results = await g.search(query="...", group_ids=[PARTITIONS.GOSLO])
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from parrot.shared.config import FalkorDBConfig, ParrotConfig

logger = logging.getLogger(__name__)

_instance = None


@dataclass(frozen=True)
class Partitions:
    """group_id constants for Graphiti multi-tenancy."""

    GOSLO = "goslo"
    MAID = "maid"
    SCENE = "scene"
    USER = "user"


PARTITIONS = Partitions()


async def get_graphiti(config: ParrotConfig | None = None):
    """Return a shared Graphiti instance (lazy singleton).

    Imports graphiti_core at call time so the rest of the codebase
    doesn't hard-depend on it (the `memory` extra may not be installed).
    """
    global _instance
    if _instance is not None:
        return _instance

    try:
        from graphiti_core import Graphiti
        from graphiti_core.driver.falkordb_driver import FalkorDriver
        from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
        from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
    except ImportError as exc:
        raise RuntimeError(
            "graphiti-core not installed. "
            "Install with: pip install -e '.[memory]'"
        ) from exc

    cfg = config or ParrotConfig()
    fdb: FalkorDBConfig = cfg.falkordb

    driver = FalkorDriver(
        host=fdb.host,
        port=fdb.port,
        database=fdb.database,
    )

    llm_client = GeminiClient(
        config=LLMConfig(
            api_key=cfg.google_api_key,
            model="gemini-2.5-flash",
        )
    )

    embedder = GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key=cfg.google_api_key,
            embedding_model="text-embedding-004",
        )
    )

    _instance = Graphiti(
        graph_driver=driver,
        llm_client=llm_client,
        embedder=embedder,
    )

    await _instance.build_indices_and_constraints()
    logger.info(
        "Graphiti initialized (FalkorDB %s:%d db=%s)",
        fdb.host, fdb.port, fdb.database,
    )
    return _instance


async def close_graphiti() -> None:
    """Shut down the Graphiti driver."""
    global _instance
    if _instance is not None:
        try:
            await _instance.close()
        except Exception:
            logger.exception("Error closing Graphiti")
        _instance = None
