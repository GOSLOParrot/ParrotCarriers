"""Environment configuration loader."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path)


_load_env()


@dataclass(frozen=True)
class RedisConfig:
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "0"))

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass(frozen=True)
class LiveKitConfig:
    url: str = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    api_key: str = os.getenv("LIVEKIT_API_KEY", "devkey")
    api_secret: str = os.getenv(
        "LIVEKIT_API_SECRET",
        "parrot_carriers_local_dev_livekit_secret_key_v1",
    )
    room_name: str = os.getenv("LIVEKIT_ROOM", "parrot-main")


@dataclass(frozen=True)
class FalkorDBConfig:
    host: str = os.getenv("FALKORDB_HOST", "localhost")
    port: int = int(os.getenv("FALKORDB_PORT", "6380"))
    database: str = os.getenv("FALKORDB_DATABASE", "parrot")


@dataclass(frozen=True)
class GeminiConfig:
    """Gemini Live (Brain voice) + reranker + embedding model selection.

    Preview 模型（*-native-audio-preview-MM-YYYY）生命周期短，通过 env 切换避免
    每次换模型都要改代码。默认值保持当前可用的 preview，若遇到 WS 1008
    policy violation 请优先把 live_model 切回稳定的 `gemini-2.0-flash-live-001`。
    """

    live_model: str = os.getenv(
        "GEMINI_LIVE_MODEL",
        "gemini-2.5-flash-native-audio-preview-12-2025",
    )
    live_voice: str = os.getenv("GEMINI_LIVE_VOICE", "Puck")
    reranker_model: str = os.getenv("GEMINI_RERANKER_MODEL", "gemini-2.5-flash")
    embedding_model: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001",
    )


@dataclass(frozen=True)
class GraphitiLLMConfig:
    """Graphiti extraction/rerank LLM provider configuration.

    Graphiti uses a separate provider choice from the live voice line. The
    default is DeepSeek for the Web Graphiti test lane, but embeddings remain
    on the existing Gemini embedder until a stable DeepSeek embedding path is
    approved. Secrets are intentionally read from env at instantiation time so
    tests and local services can override them without writing repo files.
    """

    provider: str = field(default_factory=lambda: (
        os.getenv("GRAPHITI_LLM_PROVIDER")
        or os.getenv("PARROT_GRAPHITI_LLM_PROVIDER")
        or "deepseek"
    ).strip().lower())
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = field(
        default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    )
    deepseek_model: str = field(
        default_factory=lambda: os.getenv(
            "DEEPSEEK_MODEL",
            os.getenv("GRAPHITI_DEEPSEEK_MODEL", "deepseek-v4-pro"),
        )
    )
    deepseek_small_model: str = field(
        default_factory=lambda: os.getenv(
            "DEEPSEEK_SMALL_MODEL",
            os.getenv("GRAPHITI_DEEPSEEK_SMALL_MODEL", "deepseek-v4-flash"),
        )
    )


@dataclass(frozen=True)
class ParrotConfig:
    redis: RedisConfig = field(default_factory=RedisConfig)
    livekit: LiveKitConfig = field(default_factory=LiveKitConfig)
    falkordb: FalkorDBConfig = field(default_factory=FalkorDBConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    graphiti_llm: GraphitiLLMConfig = field(default_factory=GraphitiLLMConfig)
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    debug: bool = os.getenv("PARROT_DEBUG", "false").lower() == "true"
