"""Start the Nanobot worker with ParrotCarriers Bus + WeChat channels.

Usage:
  python src/scripts/start_nanobot_worker.py            # use real nanobot gateway
  python src/scripts/start_nanobot_worker.py --stub      # use stub consumer (no LLM)
  python src/scripts/start_nanobot_worker.py --no-weixin # disable WeChat channel

This script:
  1. Resolves the parrot_config.json from the nanobot fork
  2. Injects OPENROUTER_API_KEY into the config if set
  3. Starts the nanobot gateway with parrot_bus + weixin channels

Prerequisites:
  - Redis running (docker compose -f infra/docker-compose.dev.yml up -d)
  - nanobot installed: pip install -e ../nanobot[parrot]
  - OPENROUTER_API_KEY set (or edit ~/.nanobot-parrot/config.json manually)
  - For WeChat: run 'nanobot channels login weixin' first to scan QR code
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PARROT_NANOBOT_DIR = Path.home() / ".nanobot-parrot"
FORK_CONFIG = Path(__file__).resolve().parents[3] / "nanobot" / "config" / "parrot_config.json"


def setup_config(force: bool = False, enable_weixin: bool = True) -> Path:
    """Ensure the nanobot parrot config exists. Returns path to config.json."""
    config_file = PARROT_NANOBOT_DIR / "config.json"

    if force or not config_file.exists():
        PARROT_NANOBOT_DIR.mkdir(parents=True, exist_ok=True)

        if not FORK_CONFIG.exists():
            print(f"ERROR: Config template not found at {FORK_CONFIG}")
            sys.exit(1)

        config = json.loads(FORK_CONFIG.read_text(encoding="utf-8"))

        gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        if gemini_key:
            config.setdefault("providers", {}).setdefault("gemini", {})["apiKey"] = gemini_key

        redis_url = os.getenv("REDIS_URL", "")
        if redis_url:
            config.setdefault("channels", {}).setdefault("parrot_bus", {})["redisUrl"] = redis_url

        github_token = os.getenv("GITHUB_TOKEN", "")
        if github_token:
            servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
            servers.setdefault("github", {}).setdefault("env", {})["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_token

        # Google Workspace MCP is enabled by default in parrot_config.json.
        # The MCP server manages its own OAuth state via browser login.
        # Keep its environment separate from Gemini provider credentials.
        servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
        if "google_workspace" in servers:
            servers["google_workspace"].setdefault("env", {})

        if not enable_weixin:
            channels = config.get("channels", {})
            if "weixin" in channels:
                channels["weixin"]["enabled"] = False

        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Config written to {config_file}")
    else:
        print(f"Using existing config at {config_file}")

    return config_file


def run_gateway(config_file: Path, enable_weixin: bool = True) -> None:
    """Start the nanobot gateway subprocess."""
    nanobot_exe = shutil.which("nanobot")
    if nanobot_exe is None:
        print("ERROR: 'nanobot' command not found.")
        print("  Install with: pip install -e ../nanobot[parrot]")
        sys.exit(1)

    channels = ["parrot_bus"]
    if enable_weixin:
        channels.append("weixin")

    print(f"\nStarting nanobot gateway with channels: {', '.join(channels)}")
    print(f"  Config: {config_file}")
    if enable_weixin:
        print("  WeChat: enabled (ensure QR login completed)")
    print()

    subprocess.run(
        [nanobot_exe, "gateway", "--config", str(config_file), "--verbose"],
        check=False,
    )


def run_stub() -> None:
    """Start the built-in stub consumer (no LLM, echo-only)."""
    print("\nStarting Nanobot STUB consumer (no LLM, echo-only)...")
    from parrot.bus.nanobot_consumer import run_nanobot_consumer

    asyncio.run(run_nanobot_consumer())


def main():
    parser = argparse.ArgumentParser(description="Start the Nanobot worker")
    parser.add_argument("--stub", action="store_true", help="Use stub consumer (no LLM)")
    parser.add_argument("--force-config", action="store_true", help="Regenerate config from template")
    # --no-weixin flag: 
    # Use this during P1/dev to run a pure backend Worker (parrot_bus only).
    # Omit this flag and run `nanobot channels login weixin` first if you want Maid to also chat on WeChat.
    parser.add_argument("--no-weixin", action="store_true", help="Disable WeChat channel")
    args = parser.parse_args()

    if args.stub:
        run_stub()
    else:
        enable_weixin = not args.no_weixin
        config_file = setup_config(force=args.force_config, enable_weixin=enable_weixin)
        run_gateway(config_file, enable_weixin=enable_weixin)


if __name__ == "__main__":
    main()
