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
    ARKNIGHTS_TEST = "arknights_test"
    NOBLE_ETIQUETTE = "noble_etiquette"
    LAPTOP_PROFILE_TEST = "laptop_profile_test"

    def values(self) -> list[str]:
        """Return the allowlisted Graphiti group ids."""
        return [
            self.GOSLO,
            self.MAID,
            self.SCENE,
            self.USER,
            self.ARKNIGHTS_TEST,
            self.NOBLE_ETIQUETTE,
            self.LAPTOP_PROFILE_TEST,
        ]


PARTITIONS = Partitions()

__all__ = [
    "PARTITIONS",
    "Partitions",
    "close_graphiti",
    "get_graphiti",
    "get_llm_clients",
    "graphiti_provider_status",
]


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

    llm_client, cross_encoder, provider = get_llm_clients(cfg)

    embedder = GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key=cfg.google_api_key,
            embedding_model=cfg.gemini.embedding_model,
        )
    )

    _instance = Graphiti(
        graph_driver=driver,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=cross_encoder,
    )

    await _instance.build_indices_and_constraints()
    logger.info(
        "Graphiti initialized (provider=%s FalkorDB %s:%d db=%s)",
        provider, fdb.host, fdb.port, fdb.database,
    )
    return _instance


def graphiti_provider_status(config: ParrotConfig | None = None) -> dict[str, object]:
    """Return sanitized provider status for Web/monitor routes.

    This function deliberately reports booleans instead of secrets. It also
    makes the DeepSeek -> Gemini fallback explicit so operators can tell why a
    local Graphiti run still uses Gemini.
    """
    cfg = config or ParrotConfig()
    requested = (cfg.graphiti_llm.provider or "deepseek").strip().lower()
    effective = _effective_llm_provider(cfg)
    model = (
        cfg.graphiti_llm.deepseek_model
        if effective == "deepseek"
        else cfg.gemini.reranker_model
    )
    status: dict[str, object] = {
        "requested_provider": requested,
        "provider": effective,
        "model": model,
        "secret_configured": bool(
            cfg.graphiti_llm.deepseek_api_key if effective == "deepseek" else cfg.google_api_key
        ),
        "fallback_provider": "gemini",
        "embedding_provider": "gemini",
        "embedding_model": cfg.gemini.embedding_model,
        "embedding_secret_configured": bool(cfg.google_api_key),
    }
    if effective == "deepseek":
        status["base_url"] = cfg.graphiti_llm.deepseek_base_url.rstrip("/")
        status["small_model"] = cfg.graphiti_llm.deepseek_small_model
    if requested == "deepseek" and effective != "deepseek":
        status["fallback_reason"] = (
            "deepseek_json_schema_response_format_disabled"
            if cfg.graphiti_llm.deepseek_api_key
            else "deepseek_api_key_missing"
        )
        status["deepseek_json_schema_enabled"] = (
            cfg.graphiti_llm.deepseek_json_schema_enabled
        )
    return status


def _effective_llm_provider(cfg: ParrotConfig) -> str:
    requested = (cfg.graphiti_llm.provider or "deepseek").strip().lower()
    if (
        requested == "deepseek"
        and cfg.graphiti_llm.deepseek_api_key
        and cfg.graphiti_llm.deepseek_json_schema_enabled
    ):
        return "deepseek"
    return "gemini"


def get_llm_clients(cfg: ParrotConfig):
    """Build Graphiti LLM and cross-encoder clients.

    DeepSeek is exposed through Graphiti's OpenAI-compatible generic client
    only when explicitly enabled.
    Embeddings intentionally remain Gemini-based in ``get_graphiti`` above
    because DeepSeek has not been promoted as an embedding provider for this
    repo. Graphiti's current OpenAI-compatible client sends ``json_schema`` for
    structured extraction, while DeepSeek's public API documents
    ``json_object`` JSON output. The default therefore stays on Gemini for
    extraction unless ``GRAPHITI_DEEPSEEK_JSON_SCHEMA_ENABLED`` is set.
    """
    provider = _effective_llm_provider(cfg)
    if provider == "deepseek":
        try:
            from graphiti_core.cross_encoder.openai_reranker_client import (
                OpenAIRerankerClient,
            )
            from graphiti_core.llm_client.config import LLMConfig
            from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
        except ImportError as exc:
            raise RuntimeError(
                "Graphiti OpenAI-compatible client unavailable. "
                "Install a graphiti-core version with OpenAIGenericClient."
            ) from exc

        llm_config = LLMConfig(
            api_key=cfg.graphiti_llm.deepseek_api_key,
            model=cfg.graphiti_llm.deepseek_model,
            small_model=cfg.graphiti_llm.deepseek_small_model,
            base_url=cfg.graphiti_llm.deepseek_base_url.rstrip("/"),
        )
        llm_client = OpenAIGenericClient(config=llm_config)
        return (
            llm_client,
            OpenAIRerankerClient(client=llm_client, config=llm_config),
            provider,
        )

    from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
    from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig

    gemini_config = LLMConfig(
        api_key=cfg.google_api_key,
        model=cfg.gemini.reranker_model,
    )
    return (
        GeminiClient(config=gemini_config),
        GeminiRerankerClient(config=gemini_config),
        provider,
    )


_build_llm_clients = get_llm_clients


async def close_graphiti() -> None:
    """Shut down the Graphiti driver."""
    global _instance
    if _instance is not None:
        try:
            await _instance.close()
        except Exception:
            logger.exception("Error closing Graphiti")
        _instance = None
