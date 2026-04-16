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
class ParrotConfig:
    redis: RedisConfig = field(default_factory=RedisConfig)
    livekit: LiveKitConfig = field(default_factory=LiveKitConfig)
    falkordb: FalkorDBConfig = field(default_factory=FalkorDBConfig)
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    debug: bool = os.getenv("PARROT_DEBUG", "false").lower() == "true"
