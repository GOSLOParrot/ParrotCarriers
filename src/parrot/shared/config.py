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


GEMINI_LIVE_VOICE_DEFAULT = "Aoede"
"""Default LineA Gemini Live voice for GOSLO.

LineB has its own TTS profile. This default only applies to LineA
``google.realtime.RealtimeModel`` when ``GEMINI_LIVE_VOICE`` is unset or
invalid.
"""

GEMINI_LIVE_SUPPORTED_VOICES = (
    "Zephyr",
    "Puck",
    "Charon",
    "Kore",
    "Fenrir",
    "Leda",
    "Orus",
    "Aoede",
    "Callirrhoe",
    "Autonoe",
    "Enceladus",
    "Iapetus",
    "Umbriel",
    "Algieba",
    "Despina",
    "Erinome",
    "Algenib",
    "Rasalgethi",
    "Laomedeia",
    "Achernar",
    "Alnilam",
    "Schedar",
    "Gacrux",
    "Pulcherrima",
    "Achird",
    "Zubenelgenubi",
    "Vindemiatrix",
    "Sadachbia",
    "Sadaltager",
    "Sulafat",
)


def _gemini_live_voice() -> str:
    configured = os.getenv("GEMINI_LIVE_VOICE", "").strip()
    if not configured:
        return GEMINI_LIVE_VOICE_DEFAULT
    supported_by_lower = {
        voice.lower(): voice for voice in GEMINI_LIVE_SUPPORTED_VOICES
    }
    return supported_by_lower.get(configured.lower(), GEMINI_LIVE_VOICE_DEFAULT)


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

    Preview native-audio model ids change quickly, so model selection stays
    env-configurable. LineA voice defaults to the fixed GOSLO voice above
    unless ``GEMINI_LIVE_VOICE`` names another supported Live voice.
    """

    live_model: str = os.getenv(
        "GEMINI_LIVE_MODEL",
        "gemini-2.5-flash-native-audio-preview-12-2025",
    )
    live_voice: str = field(default_factory=_gemini_live_voice)
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
    deepseek_json_schema_enabled: bool = field(
        default_factory=lambda: (
            os.getenv("GRAPHITI_DEEPSEEK_JSON_SCHEMA_ENABLED", "").strip().lower()
            in {"1", "true", "yes", "on"}
        )
    )


@dataclass(frozen=True)
class ParrotConfig:
    redis: RedisConfig = field(default_factory=RedisConfig)
    livekit: LiveKitConfig = field(default_factory=LiveKitConfig)
    falkordb: FalkorDBConfig = field(default_factory=FalkorDBConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    graphiti_llm: GraphitiLLMConfig = field(default_factory=GraphitiLLMConfig)
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    debug: bool = field(
        default_factory=lambda: os.getenv("PARROT_DEBUG", "false").lower() == "true"
    )
